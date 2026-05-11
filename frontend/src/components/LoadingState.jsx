function LoadingState({ label = 'Daten werden geladen...' }) {
  return (
    <div className="state-box state-box--loading" role="status" aria-live="polite">
      <span className="loader" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export default LoadingState;
