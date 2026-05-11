function formatPrice(amount, currency) {
  const numeric = Number(amount);

  if (!Number.isFinite(numeric)) {
    return `${amount} ${currency ?? 'EUR'}`;
  }

  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: currency ?? 'EUR',
  }).format(numeric);
}

function PriceBox({ prices = [], currency = 'EUR' }) {
  if (!prices.length) {
    return (
      <div className="price-box price-box--empty">
        Fuer dieses Produkt ist aktuell kein Demo-Preis hinterlegt.
      </div>
    );
  }

  return (
    <div className="price-grid">
      {prices.map((price, index) => {
        const label =
          price.type === 'variant'
            ? price.variant_name || price.variant_sku || 'Variante'
            : 'Produktpreis';

        return (
          <article className="price-box" key={`${price.type}-${price.variant_sku ?? index}`}>
            <div className="price-box__label">{label}</div>
            <strong>{formatPrice(price.amount, price.currency || currency)}</strong>
            {price.variant_sku ? <span>SKU: {price.variant_sku}</span> : null}
            <small>
              MwSt. {price.tax_rate ?? 'n/a'}%
              {price.price_includes_tax ? ', inklusive Steuer' : ', exklusive Steuer'}
            </small>
          </article>
        );
      })}
    </div>
  );
}

export default PriceBox;
