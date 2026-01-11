import express from "express";
import cors from "cors";
import morgan from "morgan";
import mongoose from "mongoose";
const app = express();
import userRouter from "./router/userRouter.js";
import projectRouter from "./router/projectRouter.js";
import refactorRouter from "./router/refactorRouter.js";
import globalErrorHandler from "./controller/errorController.js";

// Environment setup
const NODE_ENV = process.env.NODE_ENV || "development";
const PORT = process.env.PORT || 8000;

//middlewares
app.use(cors());
app.use(NODE_ENV === "production" ? morgan("combined") : morgan("dev"));
app.use(express.json());
app.use(express.urlencoded({ limit: "50mb", extended: true }));

// Health check endpoint
app.get("/api/v1/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date() });
});

//routes
app.use("/api/v1/user", userRouter);
app.use("/api/v1/project", projectRouter);
app.use("/api/v1/refactor", refactorRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: "Route not found" });
});

app.use(globalErrorHandler);

mongoose
  .connect(process.env.LOCAL_DB)
  .then(() => {
    console.log("[MongoDB] Connected successfully");
  })
  .catch((err) => {
    console.error("[MongoDB] Connection failed:", err.message);
    process.exit(1);
  });

process.on("unhandledRejection", (err) => {
  console.error("[Error] Unhandled Rejection:", err);
  server.close(() => {
    process.exit(1);
  });
});

process.on("uncaughtException", (err) => {
  console.error("[Error] Uncaught Exception:", err);
  server.close(() => {
    process.exit(1);
  });
});

const server = app.listen(PORT, () => {
  console.log(`[Server] Running in ${NODE_ENV} mode on port ${PORT}`);
});
