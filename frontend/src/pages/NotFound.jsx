import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <section className="page-stack page-stack--center">
      <div className="detail-panel not-found-panel">
        <span className="eyebrow">404</span>
        <h1>Seite nicht gefunden</h1>
        <p>
          Diese lokale Demo-Seite existiert nicht. Die aktuelle Foundation umfasst
          Start, Kategorien, Produkte, Produktdetails und Info.
        </p>
        <Link className="button" to="/">
          Zur Startseite
        </Link>
      </div>
    </section>
  );
}

export default NotFound;
