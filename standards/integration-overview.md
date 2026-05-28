# Integration · Schema Overview

> **Owner**: DRI
> **Last reviewed**: 2026-05-29

Multica Integrations are the team's runtime config registry. Every shared
service that needs config (MCP servers, feishu apps, autopilot bots) is an
Integration object in multica · with a typed schema · with secrets stored
encrypted.

## Why this exists
- v1 (W1) had secrets scattered in each EXEC's `.env` files · 5 places to rotate
- v2 (W5 · Plan 4-6) consolidates: one source of truth · one rotation point
- Team members no longer need to manage .env for shared services

## How to use

### As an operator (DRI)
- List schemas:  `ls standards/integration-schemas/`
- Create an integration:  see TC-3 (bootstrap script) or `multica integration create --help`
- Update config:  `multica integration set <name> <key>=<value>` (triggers hot-reload)
- Rotate secret:  `echo -n "<new>" | multica secret rotate --integration <name> <KEY> --value-stdin`

### As a service author (e.g. writing a new MCP server)
1. Pick or create a schema in `standards/integration-schemas/<your-kind>-v1.yaml`
2. Implement your server to consume `ConfigSource` (see team-context-mcp · packages/config)
3. Document your config_fields and secret_fields in the schema YAML
4. PR review the schema before deploying

## 3 kinds today

| kind | Used for | Owner |
| --- | --- | --- |
| `mcp-server` | team-context-mcp · any future MCP server | Plan 5 EXEC |
| `feishu` | (placeholder · unused in v0) | DRI |
| `autopilot-bot` | one per multica autopilot bot agent | DRI |

## Lifecycle

1. **Create**:  `multica integration create --kind mcp-server --name X --config-schema-ref mcp-server-v1 --config @c.json`
2. **Bootstrap secrets**:  `bash scripts/multica-secrets-bootstrap.sh X`
3. **Service registers**:  on boot, service POSTs to `/api/deployments`
4. **Service subscribes**:  WS for `integration.config-changed` events
5. **Hot-reload**:  `multica integration set X foo=bar` → WS event fires → service reloads
6. **Redeploy** (code change):  `multica integration redeploy X --image NEW` or rely on GitHub Actions webhook
7. **Audit**:  every config/secret access logged · `multica audit-log list --resource integration:X`

## Adding a new schema

1. Copy template:  `cp standards/integration-schemas/_template.yaml standards/integration-schemas/<kind>-v1.yaml`
2. Edit fields
3. PR review (DRI approves)
4. After merge:  schema is referenced by `config_schema_ref` when creating integrations
5. Multica web UI uses the schema for form rendering + validation
