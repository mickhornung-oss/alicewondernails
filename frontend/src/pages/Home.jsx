import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import ErrorState from '../components/ErrorState.jsx';
import LoadingState from '../components/LoadingState.jsx';
import { fetchCategories, fetchHealth } from '../api/client.js';

function Home() {
  const [health, setHealth] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    async function loadHomeData() {
      setLoading(true);
      setError('');

      try {
        const [healthData, categoryData] = await Promise.all([
          fetchHealth(),
          fetchCategories(),
        ]);

        if (!active) return;

        setHealth(healthData);
        setCategories(Array.isArray(categoryData) ? categoryData.slice(0, 4) : []);
      } catch (err) {
        if (!active) return;
        setError(err.message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadHomeData();

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="page-stack">
      <div className="hero-panel">
        <div className="hero-panel__content">
          <span className="eyebrow">Lokale Shop-Demo fuer Nail-Produkte</span>
          <h1>Alice Wonder Nails</h1>
          <p>
            Eine elegante erste Frontend-Foundation fuer den V2-Shop: Katalog,
            Kategorien, Produktdetails, Preise und lokale Info-Daten aus der
            bestehenden read-only API.
          </p>
          <div className="hero-actions">
            <Link className="button" to="/products">
              Produkte ansehen
            </Link>
            <Link className="button button--secondary" to="/categories">
              Kategorien entdecken
            </Link>
          </div>
        </div>
        <aside className="demo-card">
          <strong>Demo-/Placeholder-Daten</strong>
          <span>
            Dieser Stand ist kein Live-Shop und enthaelt keine Kauf-, Zahlungs-
            oder Checkout-Funktion.
          </span>
        </aside>
      </div>

      <section className="content-section">
        <div className="section-heading">
          <span className="eyebrow">Backend/API Status</span>
          <h2>Lokale Verbindung</h2>
        </div>

        {loading ? <LoadingState label="Healthcheck und Kategorien werden geladen..." /> : null}
        {error ? <ErrorState message={error} /> : null}

        {!loading && !error ? (
          <div className="status-grid">
            <article className="info-card">
              <span className="info-card__label">API</span>
              <strong>{health?.status ?? 'unbekannt'}</strong>
              <p>
                {health?.service ?? 'alice-wonder-nails-api'} /{' '}
                {health?.environment ?? 'local-dev'}
              </p>
            </article>
            {categories.map((category) => (
              <article className="info-card" key={category.slug}>
                <span className="info-card__label">Kategorie</span>
                <strong>{category.name}</strong>
                <p>{category.slug}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </section>
  );
}

export default Home;
