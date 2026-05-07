export const env = {
  HOST: "http://localhost:4200/", // адрес фронтенда
  API_BASE_URL: "http://localhost:8000/", // адрес апи
  KEYCLOAK_BASE_URL: "http://localhost:8155/", // адрес keycloak
  KEYCLOAK_REALM: "LOCAL", // realm из keycloak
  KEYCLOAK_CLIENT_ID: "spa-client", // client ID из keycloak
  KEYCLOAK_USES_AUTH_ENDPOINT: false, // true для старых версий keycloak
} as const;
