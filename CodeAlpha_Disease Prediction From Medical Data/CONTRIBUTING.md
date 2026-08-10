# Contributing

Contributions that improve reliability, documentation, accessibility, testing, or maintainability are welcome.

## Development Workflow

1. Create a branch from the current default branch.
2. Keep changes focused and documented.
3. Run backend tests before submitting changes.
4. Build the frontend to catch compilation issues.
5. Avoid committing `.env`, virtual environments, `node_modules`, generated build output, logs, or credentials.

Backend checks:

```powershell
cd backend
python -m pytest -q
```

Frontend check:

```powershell
cd frontend
npm run build
```

For changes to the training pipeline, include the relevant evaluation output and describe whether model artifacts were regenerated.
