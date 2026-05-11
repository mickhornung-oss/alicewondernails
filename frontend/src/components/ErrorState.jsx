function ErrorState({
  title = 'Daten konnten nicht geladen werden',
  message,
  children,
}) {
  return (
    <div className="state-box state-box--error" role="alert">
      <strong>{title}</strong>
      {message ? <span>{message}</span> : null}
      <small>
        Pruefe bei lokaler Entwicklung, ob das Django-Backend gestartet ist und
        Demo-Daten importiert wurden.
      </small>
      {children}
    </div>
  );
}

export default ErrorState;
