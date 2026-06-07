"""
定时任务：自动取消超时未支付订单
=================================

策略：
    - 商城订单(ShopOrder)：status=0 且创建超过 UNPAID_EXPIRE_HOURS 小时 → status=4(已取消)
    - 接送机订单(TransferOrder)：status=0 且创建超过 UNPAID_EXPIRE_HOURS 小时 → status=3(已取消)
    - 门票订单(TicketOrder)：status=0 且创建超过 UNPAID_EXPIRE_HOURS 小时 → status=3(已取消)

启动方式：
    在 create_app() 中调用 init_scheduler(app) 即可，只有非 DEBUG 模式
    或环境变量 ENABLE_SCHEDULER=1 时才会启动（避免开发时重复执行）。

运行间隔：
    默认每 30 分钟扫描一次（可通过 SCHEDULER_INTERVAL_MINUTES 环境变量调整）。
"""

import os
import logging
from datetime import timedelta
from threading import Thread
import time

logger = logging.getLogger(__name__)

# 默认超时小时数（可通过环境变量覆盖）
UNPAID_EXPIRE_HOURS = int(os.getenv('UNPAID_EXPIRE_HOURS', '24'))
# 扫描间隔（分钟）
SCHEDULER_INTERVAL_MINUTES = int(os.getenv('SCHEDULER_INTERVAL_MINUTES', '30'))


def cancel_expired_unpaid_orders(app):
    """扫描并取消所有超时未支付订单"""
    from app import db
    from app.models import ShopOrder, TransferOrder, TicketOrder, TicketPackage, china_now

    now = china_now()
    cutoff = now - timedelta(hours=UNPAID_EXPIRE_HOURS)
    total_cancelled = 0

    with app.app_context():
        try:
            # ===== 商城订单：status=0 且创建时间 < cutoff =====
            shop_orders = ShopOrder.query.filter(
                ShopOrder.status == 0,
                ShopOrder.created_at < cutoff
            ).all()
            for order in shop_orders:
                order.status = 4  # 已取消
                order.cancelled_at = now
                order.refund_status = 0
                order.refund_amount = 0
                total_cancelled += 1

            # ===== 接送机订单：status=0 且创建时间 < cutoff =====
            transfer_orders = TransferOrder.query.filter(
                TransferOrder.status == 0,
                TransferOrder.created_at < cutoff
            ).all()
            for order in transfer_orders:
                order.status = 3  # 已取消
                order.cancelled_at = now
                order.refund_status = 0
                order.refund_amount = 0
                total_cancelled += 1

            # ===== 门票订单：status=0 且创建时间 < cutoff =====
            ticket_orders = TicketOrder.query.filter(
                TicketOrder.status == 0,
                TicketOrder.created_at < cutoff
            ).all()
            for order in ticket_orders:
                order.status = 3  # 已取消
                order.cancelled_at = now
                order.refund_status = 0
                order.refund_amount = 0
                total_cancelled += 1

                # 恢复门票配额
                if order.package_snapshot:
                    snapshots = order.package_snapshot if isinstance(order.package_snapshot, list) else [order.package_snapshot]
                    for item in snapshots:
                        if not isinstance(item, dict):
                            continue
                        pkg_id = item.get('package_id')
                        quantity = item.get('quantity', 0)
                        if pkg_id and quantity:
                            pkg = TicketPackage.query.get(pkg_id)
                            if pkg and pkg.inventory_mode == 'manual_quota':
                                pkg.quota_used = max((pkg.quota_used or 0) - quantity, 0)

            if total_cancelled > 0:
                db.session.commit()
                logger.info(
                    f'[scheduler] 已自动取消 {total_cancelled} 个超时未支付订单 '
                    f'(shop={len(shop_orders)}, transfer={len(transfer_orders)}, ticket={len(ticket_orders)})'
                )
        except Exception as e:
            db.session.rollback()
            logger.error(f'[scheduler] 取消超时订单失败: {e}', exc_info=True)


def _scheduler_loop(app):
    """后台线程主循环"""
    interval = SCHEDULER_INTERVAL_MINUTES * 60  # 转为秒
    logger.info(
        f'[scheduler] 定时任务已启动：每 {SCHEDULER_INTERVAL_MINUTES} 分钟扫描一次，'
        f'超过 {UNPAID_EXPIRE_HOURS} 小时未支付的订单将被自动取消'
    )

    while True:
        try:
            cancel_expired_unpaid_orders(app)
        except Exception as e:
            logger.error(f'[scheduler] 未预期的错误: {e}', exc_info=True)
        time.sleep(interval)


def init_scheduler(app):
    """初始化定时任务（在 create_app 中调用）

    仅在以下情况启动：
    1. 环境变量 ENABLE_SCHEDULER=1（显式开启）
    2. 非 DEBUG 模式时自动开启

    设置 ENABLE_SCHEDULER=0 可强制关闭。
    """
    enable = os.getenv('ENABLE_SCHEDULER', '')
    if enable == '0':
        return
    if enable != '1' and app.config.get('DEBUG'):
        app.logger.info('[scheduler] DEBUG 模式下未启用定时任务（设置 ENABLE_SCHEDULER=1 可强制开启）')
        return

    thread = Thread(target=_scheduler_loop, args=(app,), daemon=True)
    thread.start()
    app.logger.info('[scheduler] 后台定时任务线程已启动')
