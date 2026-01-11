module.exports = {
  apps: [
    {
      name: "python-backend",
      script: "app.py",
      cwd: "/var/www/code-smell/python-backend",
      interpreter: "/var/www/code-smell/python-backend/venv/bin/python",
      instances: 1,
      exec_mode: "fork",
      env: {
        FLASK_ENV: "production",
        FLASK_DEBUG: "0",
      },
      error_file: "./logs/python-backend-error.log",
      out_file: "./logs/python-backend-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    },
    {
      name: "node-backend",
      script: "index.js",
      cwd: "/var/www/code-smell/node-backend",
      instances: 2,
      exec_mode: "cluster",
      env: {
        NODE_ENV: "production",
        PORT: 8000,
      },
      error_file: "./logs/node-backend-error.log",
      out_file: "./logs/node-backend-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    },
    {
      name: "nextjs-frontend",
      script: "node_modules/.bin/next",
      args: "start",
      cwd: "/var/www/code-smell/frontend",
      instances: 2,
      exec_mode: "cluster",
      env: {
        NODE_ENV: "production",
        PORT: 3000,
      },
      error_file: "./logs/nextjs-error.log",
      out_file: "./logs/nextjs-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    },
  ],
};
