import { Link } from 'react-router-dom';

function ProductCard({ product }) {
  const categoryName = product.category?.name ?? 'Ohne Kategorie';
  const variantCount = product.variants?.length ?? 0;

  return (
    <article className="product-card">
      <div className="product-card__meta">{categoryName}</div>
      <h3>{product.name}</h3>
      <p>{product.short_description || 'Demo-Produkt ohne Kurzbeschreibung.'}</p>
      <div className="product-card__facts">
        <span>{variantCount} Variante{variantCount === 1 ? '' : 'n'}</span>
        {product.category?.slug ? <span>{product.category.slug}</span> : null}
      </div>
      <Link className="button button--secondary" to={`/products/${product.slug}`}>
        Details ansehen
      </Link>
    </article>
  );
}

export default ProductCard;
