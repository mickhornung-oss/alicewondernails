const DEFAULT_CUSTOMER_GROUP = 'b2c';
const DEFAULT_COUNTRY = 'DE';

function buildQuery(params) {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, value);
    }
  });

  const query = search.toString();
  return query ? `?${query}` : '';
}

function getErrorMessage(payload, fallback) {
  if (payload?.error?.message) {
    return payload.error.message;
  }

  if (payload?.detail) {
    return payload.detail;
  }

  return fallback;
}

export async function requestJson(path) {
  try {
    const response = await fetch(path, {
      headers: {
        Accept: 'application/json',
      },
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      throw new Error('Die API-Antwort konnte nicht als JSON gelesen werden.');
    }

    if (!response.ok) {
      throw new Error(
        getErrorMessage(payload, `API-Anfrage fehlgeschlagen (${response.status}).`),
      );
    }

    if (payload && payload.success === false) {
      throw new Error(getErrorMessage(payload, 'Die API hat einen Fehler gemeldet.'));
    }

    if (payload && Object.prototype.hasOwnProperty.call(payload, 'data')) {
      return payload.data;
    }

    return payload;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        'Die lokale API ist aktuell nicht erreichbar. Bitte pruefe, ob das Django-Backend laeuft.',
      );
    }

    if (error instanceof Error) {
      throw new Error(error.message);
    }

    throw new Error('Die lokale API ist aktuell nicht erreichbar.');
  }
}

export function fetchHealth() {
  return requestJson('/api/v1/health/');
}

export function fetchCategories() {
  return requestJson('/api/v1/catalog/categories/');
}

export function fetchProducts(customerGroup = DEFAULT_CUSTOMER_GROUP) {
  return requestJson(
    `/api/v1/catalog/products/${buildQuery({ customer_group: customerGroup })}`,
  );
}

export function fetchProductDetail(slug, customerGroup = DEFAULT_CUSTOMER_GROUP) {
  return requestJson(
    `/api/v1/catalog/products/${encodeURIComponent(slug)}/${buildQuery({
      customer_group: customerGroup,
    })}`,
  );
}

export function fetchProductPrices(slug, customerGroup = DEFAULT_CUSTOMER_GROUP) {
  return requestJson(
    `/api/v1/pricing/products/${encodeURIComponent(slug)}/prices/${buildQuery({
      customer_group: customerGroup,
    })}`,
  );
}

export function fetchShippingMethods(
  customerGroup = DEFAULT_CUSTOMER_GROUP,
  country = DEFAULT_COUNTRY,
) {
  return requestJson(
    `/api/v1/shipping/methods/${buildQuery({
      customer_group: customerGroup,
      country,
    })}`,
  );
}

export function fetchPaymentMethods(customerGroup = DEFAULT_CUSTOMER_GROUP) {
  return requestJson(
    `/api/v1/payments/methods/${buildQuery({ customer_group: customerGroup })}`,
  );
}

export function fetchLegalDocuments(customerGroup = DEFAULT_CUSTOMER_GROUP) {
  return requestJson(
    `/api/v1/legal/active/${buildQuery({ customer_group: customerGroup })}`,
  );
}
