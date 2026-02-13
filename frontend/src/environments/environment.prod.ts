export const env = {
  HOST: "http://localhost:4200/",
  API_BASE_URL: "http://localhost:8000/",
  KEYCLOAK_BASE_URL: "http://localhost:8155/",
  KEYCLOAK_REALM: "LOCAL",
  KEYCLOAK_CLIENT_ID: "spa-client",
  KEYCLOACK_USES_AUTH_ENDPOINT: false,
} as const;
