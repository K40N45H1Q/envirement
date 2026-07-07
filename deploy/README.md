# Production deployment

## Nginx

Copy `deploy/nginx/cvhold.com.conf` to:

`/etc/nginx/sites-available/app`

Then make sure `/etc/nginx/sites-enabled/app` points to it and reload nginx:

```bash
ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
nginx -t
systemctl reload nginx
```

## Backend service

Copy `deploy/systemd/cvhold-backend.service` to:

`/etc/systemd/system/cvhold-backend.service`

Then enable and restart it:

```bash
systemctl daemon-reload
systemctl enable cvhold-backend
systemctl restart cvhold-backend
systemctl status cvhold-backend
```

## Frontend publish path

The production nginx config serves the built frontend from:

`/var/www/app/frontend`

Build the frontend from the repository root:

```bash
cd frontend
npm install
npm run build
```

Deploy the generated `frontend/dist` contents into:

`/var/www/app/frontend`

## Backend expectations

The backend is proxied only through:

- `/api/`
- `/uploads/`

This keeps production routing consistent with local development and avoids root-level auth endpoint drift.
