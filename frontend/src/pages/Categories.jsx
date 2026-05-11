import { useEffect, useState } from 'react';
import ErrorState from '../components/ErrorState.jsx';
import LoadingState from '../components/LoadingState.jsx';
import { fetchCategories } from '../api/client.js';

function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    fetchCategories()
      .then((data) => {
        if (active) {
          setCategories(Array.isArray(data) ? data : []);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="page-stack">
      <div className="section-heading">
        <span className="eyebrow">Katalogstruktur</span>
        <h1>Kategorien</h1>
        <p>Read-only Kategorien aus der lokalen Backend-API.</p>
      </div>

      {loading ? <LoadingState label="Kategorien werden geladen..." /> : null}
      {error ? <ErrorState message={error} /> : null}

      {!loading && !error ? (
        <div className="card-grid">
          {categories.map((category) => (
            <article className="info-card" key={category.slug}>
              <span className="info-card__label">Sortierung {category.sort_order}</span>
              <strong>{category.name}</strong>
              <p>{category.description || `Slug: ${category.slug}`}</p>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}

export default Categories;
