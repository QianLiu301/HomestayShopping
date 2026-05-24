export const USD_CNY_RATE = 7.2

const usdCurrencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

export function formatUsdReference(price) {
  const numericPrice = Number(price)
  if (!Number.isFinite(numericPrice) || numericPrice <= 0) return ''
  return usdCurrencyFormatter.format(numericPrice / USD_CNY_RATE)
}
