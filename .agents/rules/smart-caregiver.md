# SmartCaregiver Project Standards

This document defines the coding standards and architectural rules for the SmartCaregiver project, utilizing Flutter (GetX) for the frontend and FastAPI for the backend.

## 1. Frontend: Flutter with GetX Pattern

### 1.1 State Management & Controllers
- **Reactive Variables**: Use `.obs` for state variables. Wrap variables with `Rx<T>` for complex objects.
- **Encapsulation**: Make reactive variables private (e.g., `_user.obs`) and expose them via public getters (`User get user => _user.value`).
- **Separation of Concerns**: Controllers should handle state and coordinate with use cases or repositories. Business logic should reside in use cases/services, not directly inside the controller.
- **Workers**: Use `debounce` for search inputs, `ever` for side effects, `once` for one-time initialization, and `interval` for periodic updates. Always clean up workers in `onClose()`.
- **Lifecycle**: Perform initial loading in `onInit()`, UI-dependent actions in `onReady()`, and clean up resources (streams, subscriptions, workers) in `onClose()`.

### 1.2 Dependency Injection & Bindings
- **Bindings**: Create a `Bindings` class for each feature/route. Use `Get.lazyPut()` for dependencies that should be instantiated only when needed. Use `Get.put()` for singletons needed immediately.
- **Services**: Use `GetxService` for permanent, app-wide services (e.g., AuthService, ThemeService, StorageService). Register them with `permanent: true`.
- **Controllers**: Avoid instantiating controllers directly in the UI. Always use bindings to manage controller lifecycles.

### 1.3 Networking with GetConnect
- Use `GetConnect` as the standard HTTP client.
- Create an `ApiProvider` extending `GetConnect` to configure the `baseUrl`, default timeouts, and interceptors (for authentication headers, logging, and token refresh).
- Keep API interactions abstracted behind repositories.

### 1.4 Routing & Navigation
- Define all routes centrally in an `AppRoutes` class.
- Use named routes (e.g., `Get.toNamed('/route')`) with associated `Bindings` and `middlewares` to enforce rules like authentication.
- Avoid anonymous routing (e.g., `Get.to(() => Page())`) in complex flows to ensure bindings are properly attached.

### 1.5 UI & Widgets
- Use `Obx` for simple localized state updates, and `GetX` when dependency injection is needed inside the widget.
- UI should be completely devoid of business logic.
- Replace deprecated Flutter APIs immediately (e.g., use `.withValues()` instead of `.withOpacity()`, `initialValue` instead of `value` in form fields).

---

## 2. Backend: FastAPI with Pydantic V2

### 2.1 Async Python & Endpoints
- **Async Execution**: Use `async def` for all endpoint definitions, and strictly use async alternatives for I/O bound tasks, including SQLAlchemy database interactions.
- **Dependencies**: Use `Annotated[T, Depends(...)]` for dependency injection (e.g., getting DB sessions or the current authenticated user).
- **Type Hinting**: Heavily enforce type hints across the entire codebase. Use `X | None` instead of `Optional[X]`.

### 2.2 Pydantic V2 Validation
- **Schemas**: Define strict Pydantic V2 models for incoming payloads and outgoing responses (`response_model`).
- **Validation**: Use `@field_validator` and `@model_validator` for custom validation logic.
- **Config**: Use `model_config = model_config(...)` to enforce strict parsing (e.g., `str_strip_whitespace=True`, `from_attributes=True` for ORM serialization).

### 2.3 Database (SQLAlchemy Async)
- **Async DB**: Only use `AsyncSession` and `select()` for database queries. Never use synchronous `Session` or blocking I/O calls.
- **CRUD Abstraction**: Separate CRUD operations from endpoint handlers. Create dedicated functions in `crud.py` or a specific repository layer.

### 2.4 Authentication & Security
- **JWT Authentication**: Implement token-based authentication using `OAuth2PasswordBearer` and `jose.jwt`. Ensure secrets are managed via environment variables.
- **Authorization**: Protect endpoints using an injected `get_current_user` dependency.

### 2.5 Testing
- **Async Testing**: Write tests using `pytest` and `httpx`. Ensure test DB sessions are properly mocked or isolated.
- **Coverage**: Verify endpoint behavior, schema validation, and ensure OpenAPI documentation is generated correctly at `/docs`.

## 3. General Rules
- Clean up any dead code, unused imports, or empty methods.
- Document complex logic, use cases, and non-trivial patterns.
- Follow a modular architecture separating features into distinct modules (e.g., Domain, Data, Presentation layers).
