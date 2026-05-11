import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Start' },
  { to: '/categories', label: 'Kategorien' },
  { to: '/products', label: 'Produkte' },
  { to: '/info', label: 'Info' },
];

function Header() {
  return (
    <header className="site-header">
      <NavLink className="brand" to="/" aria-label="Alice Wonder Nails Startseite">
        <span className="brand__mark">AWN</span>
        <span>
          <span className="brand__name">Alice Wonder Nails</span>
          <span className="brand__subline">Lokale Shop-Demo</span>
        </span>
      </NavLink>

      <nav className="main-nav" aria-label="Hauptnavigation">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive ? 'main-nav__link main-nav__link--active' : 'main-nav__link'
            }
            end={item.to === '/'}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="demo-pill">Demo / kein Live-Shop</div>
    </header>
  );
}

export default Header;
