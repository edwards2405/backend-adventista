# 🏥 HAV Portal — Especificación de Endpoints API REST

> **Proyecto**: Hospital Adventista de Venezuela — Sistema de Gestión Hospitalaria  
> **Frontend**: React + Vite (ya construido)  
> **Estado actual**: Todo el frontend usa datos mock locales (`src/data/mockData.js`). Se necesita un backend real con estos endpoints para que el sistema quede funcional profesionalmente.  
> **Base URL sugerida**: `VITE_API_BASE_URL` → ejemplo: `https://api.hav.edu.ve/api/v1`

---

## 📋 Índice

1. [Modelos de Datos (Schemas)](#1-modelos-de-datos-schemas)
2. [Autenticación](#2-autenticación)
3. [Pacientes](#3-pacientes)
4. [Citas (Appointments)](#4-citas-appointments)
5. [Personal (Staff)](#5-personal-staff)
6. [Historia Clínica](#6-historia-clínica)
7. [Dashboard / Estadísticas](#7-dashboard--estadísticas)
8. [Actividad Reciente](#8-actividad-reciente)
9. [Notas Técnicas](#9-notas-técnicas)

---

## 1. Modelos de Datos (Schemas)

Estos son los modelos exactos que el frontend espera recibir. El backend debe respetar estos campos.

### 🔹 User

```json
{
  "id": "u1",
  "email": "admin@hav.edu.ve",
  "role": "superadmin | recepcion | medico",
  "name": "Dr. Rodríguez",
  "title": "Director General",
  "avatar": "DR"
}
```

> [!IMPORTANT]
> Los roles válidos son exactamente: `superadmin`, `recepcion`, `medico`. El frontend usa estos valores para determinar rutas, permisos y vistas visibles.

### 🔹 Patient

```json
{
  "id": "p1",
  "cedula": "V-12.345.678",
  "name": "Eduardo San Vicente",
  "age": 45,
  "gender": "Masculino | Femenino",
  "phone": "+58 412-555-0101",
  "email": "e.sanvicente@gmail.com",
  "dob": "1979-03-14",
  "alergias": ["Penicilina", "Sulfa"],
  "status": "activo | pendiente | dado_de_alta",
  "bloodType": "O+ | O- | A+ | A- | B+ | B- | AB+ | AB-",
  "insurance": "PDVSA · Póliza Oro",
  "lastVisit": "2026-04-19",
  "doctor": "Dr. Ricardo Pérez",
  "specialty": "Cardiología",
  "vitalSigns": {
    "bp": "120/80",
    "hr": 72,
    "temp": 36.5,
    "spo2": 98,
    "weight": 82,
    "bmi": 24.5
  }
}
```

### 🔹 Appointment

```json
{
  "id": "a1",
  "patientId": "p1",
  "patientName": "Eduardo San Vicente",
  "doctor": "Dr. Ricardo Pérez",
  "specialty": "Cardiología",
  "date": "2026-04-21",
  "time": "08:00",
  "status": "confirmada | en_espera | pendiente | completada",
  "type": "Control | Consulta Nueva | Primera Vez | Urgencia"
}
```

### 🔹 Staff

```json
{
  "id": "s1",
  "name": "Marcos Arévalo",
  "email": "marcos@hav.edu.ve",
  "role": "recepcion | enfermeria | administrativo | medico",
  "status": "activo | inactivo",
  "since": "2021-03-01"
}
```

### 🔹 Clinical History Record

```json
{
  "id": "h1",
  "patientId": "p1",
  "date": "2026-04-14",
  "doctor": "Dr. Ricardo Pérez",
  "diagnosis": "Hipertensión arterial controlada",
  "soap": {
    "subjetivo": "Paciente refiere cefalea ocasional",
    "objetivo": "TA 128/82, FC 74",
    "analisis": "Hipertensión leve, bajo control farmacológico",
    "plan": "Continuar Losartán 50mg, control en 4 semanas"
  },
  "status": "abierta | cerrada"
}
```

### 🔹 Recent Activity

```json
{
  "id": "r1",
  "user": "Marcos Arévalo",
  "action": "Registró cita",
  "detail": "Eduardo San Vicente · 08:00",
  "time": "hace 5 min",
  "avatar": "MA"
}
```

---

## 2. Autenticación

Consumido por: [LoginScreen.jsx](file:///c:/workspace/Project-IV-main/src/views/LoginScreen.jsx)

---

### `POST /api/v1/auth/login`

Inicia sesión con credenciales del usuario.

**Request Body:**
```json
{
  "email": "admin@hav.edu.ve",
  "password": "admin123"
}
```

**Response 200 (éxito):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "u1",
    "email": "admin@hav.edu.ve",
    "role": "superadmin",
    "name": "Dr. Rodríguez",
    "title": "Director General",
    "avatar": "DR"
  }
}
```

**Response 401 (credenciales inválidas):**
```json
{
  "success": false,
  "message": "Credenciales incorrectas"
}
```

> [!NOTE]
> El frontend actualmente valida contra un array local `USERS`. Reemplazar con esta llamada API. El token JWT retornado debe enviarse en headers `Authorization: Bearer <token>` en todas las demás peticiones.

---

### `POST /api/v1/auth/logout`

Cierra la sesión del usuario (opcional, según implementación de tokens).

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "Sesión cerrada"
}
```

---

### `GET /api/v1/auth/me`

Obtiene el perfil del usuario autenticado (para validar sesión activa al recargar página).

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "user": {
    "id": "u1",
    "email": "admin@hav.edu.ve",
    "role": "superadmin",
    "name": "Dr. Rodríguez",
    "title": "Director General",
    "avatar": "DR"
  }
}
```

---

## 3. Pacientes

Consumido por: [PatientsView.jsx](file:///c:/workspace/Project-IV-main/src/views/shared/PatientsView.jsx), [MedicoDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/medico/MedicoDashboard.jsx), [CalendarView.jsx](file:///c:/workspace/Project-IV-main/src/views/shared/CalendarView.jsx)

---

### `GET /api/v1/patients`

Lista todos los pacientes. Soporta búsqueda por nombre o cédula.

**Headers:** `Authorization: Bearer <token>`

**Query Params (opcionales):**
| Param    | Tipo   | Descripción                          |
|----------|--------|--------------------------------------|
| `search` | string | Buscar por nombre o cédula           |
| `status` | string | Filtrar: `activo`, `pendiente`, `dado_de_alta` |
| `page`   | number | Paginación (default: 1)              |
| `limit`  | number | Resultados por página (default: 20)  |

**Response 200:**
```json
{
  "success": true,
  "data": [ /* array de Patient objects */ ],
  "total": 6,
  "page": 1,
  "totalPages": 1
}
```

---

### `GET /api/v1/patients/:id`

Obtiene un paciente específico con todos sus datos (signos vitales incluidos).

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": { /* Patient object completo */ }
}
```

---

### `POST /api/v1/patients`

Registra un nuevo paciente. Usado por el rol `recepcion`.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Nuevo Paciente",
  "cedula": "V-30.000.000",
  "age": 35,
  "phone": "+58 412-000-0000",
  "gender": "Masculino",
  "bloodType": "O+",
  "insurance": "Sin seguro",
  "email": "",
  "dob": ""
}
```

**Response 201:**
```json
{
  "success": true,
  "data": { /* Patient object creado con id generado */ }
}
```

> [!IMPORTANT]
> Solo el rol `recepcion` puede crear pacientes. El frontend muestra el botón "Nuevo Paciente" solo para ese rol.

---

### `PUT /api/v1/patients/:id`

Actualiza datos de un paciente existente.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** (campos parciales permitidos)
```json
{
  "phone": "+58 414-999-9999",
  "insurance": "Seguros Caracas",
  "status": "dado_de_alta"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": { /* Patient object actualizado */ }
}
```

---

### `PUT /api/v1/patients/:id/vital-signs`

Actualiza los signos vitales de un paciente.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "bp": "130/85",
  "hr": 78,
  "temp": 36.8,
  "spo2": 97,
  "weight": 80,
  "bmi": 24.0
}
```

**Response 200:**
```json
{
  "success": true,
  "data": { /* vitalSigns actualizados */ }
}
```

---

## 4. Citas (Appointments)

Consumido por: [CalendarView.jsx](file:///c:/workspace/Project-IV-main/src/views/shared/CalendarView.jsx), [RecepcionDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/recepcion/RecepcionDashboard.jsx), [SuperAdminDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/superadmin/SuperAdminDashboard.jsx), [MedicoDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/medico/MedicoDashboard.jsx)

---

### `GET /api/v1/appointments`

Lista todas las citas. Soporta filtros por fecha, estado y doctor.

**Headers:** `Authorization: Bearer <token>`

**Query Params (opcionales):**
| Param      | Tipo   | Descripción                                    |
|------------|--------|------------------------------------------------|
| `date`     | string | Filtrar por fecha exacta: `2026-04-21`         |
| `dateFrom` | string | Rango desde                                    |
| `dateTo`   | string | Rango hasta                                    |
| `status`   | string | `confirmada`, `en_espera`, `pendiente`, `completada` |
| `doctor`   | string | Nombre del doctor                              |
| `month`    | number | Mes (1-12) para vista calendario               |
| `year`     | number | Año para vista calendario                      |

**Response 200:**
```json
{
  "success": true,
  "data": [ /* array de Appointment objects */ ],
  "total": 6
}
```

> [!NOTE]
> El `CalendarView` necesita todas las citas del mes actual para pintar los puntos indicadores en cada día del calendario. El endpoint debe aceptar filtro por `month` y `year`.

---

### `GET /api/v1/appointments/:id`

Obtiene una cita específica.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": { /* Appointment object */ }
}
```

---

### `POST /api/v1/appointments`

Crea una nueva cita. Usado por el rol `recepcion`.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "patientId": "p1",
  "doctor": "Dr. Ricardo Pérez",
  "specialty": "Cardiología",
  "date": "2026-04-25",
  "time": "08:00",
  "type": "Consulta Nueva"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "a7",
    "patientId": "p1",
    "patientName": "Eduardo San Vicente",
    "doctor": "Dr. Ricardo Pérez",
    "specialty": "Cardiología",
    "date": "2026-04-25",
    "time": "08:00",
    "status": "pendiente",
    "type": "Consulta Nueva"
  }
}
```

> [!IMPORTANT]
> El backend debe resolver el `patientName` a partir del `patientId`. El status inicial siempre es `pendiente`. Solo `recepcion` puede crear citas.

---

### `PATCH /api/v1/appointments/:id/status`

Cambia el estado de una cita (confirmar, completar, etc.).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "confirmada"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": { /* Appointment object actualizado */ }
}
```

> [!NOTE]
> Este endpoint se usa en dos lugares:
> - `RecepcionDashboard`: botón "Confirmar" para citas en espera/pendientes
> - `CalendarView`: icono ✅ para confirmar citas pendientes
> 
> Transiciones de estado válidas: `pendiente → confirmada`, `confirmada → completada`, `en_espera → confirmada`

---

### `DELETE /api/v1/appointments/:id`

Cancela/elimina una cita (para futuras implementaciones).

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "Cita eliminada"
}
```

---

## 5. Personal (Staff)

Consumido por: [StaffManagement.jsx](file:///c:/workspace/Project-IV-main/src/views/superadmin/StaffManagement.jsx), [SuperAdminDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/superadmin/SuperAdminDashboard.jsx)

---

### `GET /api/v1/staff`

Lista todo el personal del hospital. Soporta búsqueda.

**Headers:** `Authorization: Bearer <token>`

**Query Params (opcionales):**
| Param    | Tipo   | Descripción                      |
|----------|--------|----------------------------------|
| `search` | string | Buscar por nombre o correo       |
| `role`   | string | Filtrar: `recepcion`, `enfermeria`, `administrativo`, `medico` |
| `status` | string | `activo`, `inactivo`             |

**Response 200:**
```json
{
  "success": true,
  "data": [ /* array de Staff objects */ ],
  "total": 6
}
```

---

### `POST /api/v1/staff`

Registra un nuevo miembro del personal. Solo `superadmin`.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Nuevo Empleado",
  "email": "nuevo@hav.edu.ve",
  "role": "recepcion",
  "status": "activo"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "s7",
    "name": "Nuevo Empleado",
    "email": "nuevo@hav.edu.ve",
    "role": "recepcion",
    "status": "activo",
    "since": "2026-04-21"
  }
}
```

---

### `PUT /api/v1/staff/:id`

Edita un miembro del personal (cambio de rol, datos, etc.). Solo `superadmin`.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** (campos parciales permitidos)
```json
{
  "role": "medico"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": { /* Staff object actualizado */ }
}
```

> [!NOTE]
> El panel lateral de edición en `StaffManagement` actualmente solo permite cambiar el rol. Pero conviene que el endpoint acepte actualizar cualquier campo.

---

### `PATCH /api/v1/staff/:id/status`

Activa/desactiva un miembro del personal (toggle habilitado). Solo `superadmin`.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "inactivo"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": { /* Staff object actualizado */ }
}
```

> [!IMPORTANT]
> Este endpoint corresponde al toggle switch en la tabla de `StaffManagement`. Alterna entre `activo` ↔ `inactivo`.

---

### `DELETE /api/v1/staff/:id`

Elimina un miembro del personal. Solo `superadmin`.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "Miembro del personal eliminado"
}
```

---

## 6. Historia Clínica

Consumido por: [MedicoDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/medico/MedicoDashboard.jsx)

---

### `GET /api/v1/clinical-history?patientId=:patientId`

Obtiene el historial clínico de un paciente específico.

**Headers:** `Authorization: Bearer <token>`

**Query Params:**
| Param       | Tipo   | Descripción                | Requerido |
|-------------|--------|----------------------------|-----------|
| `patientId` | string | ID del paciente            | ✅ Sí      |
| `status`    | string | `abierta`, `cerrada`       | No        |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "h1",
      "patientId": "p1",
      "date": "2026-04-14",
      "doctor": "Dr. Ricardo Pérez",
      "diagnosis": "Hipertensión arterial controlada",
      "soap": {
        "subjetivo": "Paciente refiere cefalea ocasional",
        "objetivo": "TA 128/82, FC 74",
        "analisis": "Hipertensión leve, bajo control farmacológico",
        "plan": "Continuar Losartán 50mg, control en 4 semanas"
      },
      "status": "cerrada"
    }
  ]
}
```

---

### `POST /api/v1/clinical-history`

Guarda una nueva entrada de historia clínica (nota SOAP). Solo `medico`.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "patientId": "p1",
  "diagnosis": "Hipertensión arterial controlada",
  "soap": {
    "subjetivo": "Paciente refiere cefalea ocasional",
    "objetivo": "TA 128/82, FC 74",
    "analisis": "Hipertensión leve, bajo control farmacológico",
    "plan": "Continuar Losartán 50mg, control en 4 semanas"
  }
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "h4",
    "patientId": "p1",
    "date": "2026-04-21",
    "doctor": "Dr. Ricardo Pérez",
    "diagnosis": "Hipertensión arterial controlada",
    "soap": { ... },
    "status": "abierta"
  }
}
```

> [!IMPORTANT]
> El campo `doctor` debe resolverse desde el token del usuario autenticado, NO enviarse desde el frontend. La `date` se genera en el backend. El `status` inicial es siempre `abierta`.

---

### `PATCH /api/v1/clinical-history/:id/status`

Cierra o reabre una historia clínica.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "cerrada"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": { /* Clinical History object actualizado */ }
}
```

---

## 7. Dashboard / Estadísticas

Consumido por: [SuperAdminDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/superadmin/SuperAdminDashboard.jsx), [RecepcionDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/recepcion/RecepcionDashboard.jsx)

---

### `GET /api/v1/dashboard/superadmin`

Estadísticas generales del sistema. Solo `superadmin`.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "patientsAttendedToday": 1284,
    "patientsAttendedDelta": "+12%",
    "activeStaffCount": 5,
    "totalStaffCount": 6,
    "scheduledAppointments": 6,
    "newRegistrations": 12,
    "specialtyFlow": [
      { "name": "Cardiología", "count": 38, "max": 50 },
      { "name": "Medicina Interna", "count": 24, "max": 50 },
      { "name": "Ginecología", "count": 19, "max": 50 },
      { "name": "Pediatría", "count": 15, "max": 50 },
      { "name": "Traumatología", "count": 11, "max": 50 }
    ],
    "monthlyAppointments": {
      "current": 1847,
      "target": 2500
    }
  }
}
```

---

### `GET /api/v1/dashboard/recepcion`

Estadísticas del día para recepción. Solo `recepcion`.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "todayAppointments": 4,
    "confirmedCount": 3,
    "waitingCount": 1,
    "attendedCount": 18
  }
}
```

> [!NOTE]
> Alternativamente, el frontend puede calcular estas estadísticas a partir del endpoint `GET /api/v1/appointments?date=today`. Es decisión del backend si centralizar o no.

---

## 8. Actividad Reciente

Consumido por: [SuperAdminDashboard.jsx](file:///c:/workspace/Project-IV-main/src/views/superadmin/SuperAdminDashboard.jsx)

---

### `GET /api/v1/activity`

Obtiene las acciones recientes del sistema.

**Headers:** `Authorization: Bearer <token>`

**Query Params (opcionales):**
| Param   | Tipo   | Descripción                   |
|---------|--------|-------------------------------|
| `limit` | number | Cantidad de registros (default: 10) |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "r1",
      "user": "Marcos Arévalo",
      "action": "Registró cita",
      "detail": "Eduardo San Vicente · 08:00",
      "time": "hace 5 min",
      "avatar": "MA"
    }
  ]
}
```

---

### `GET /api/v1/doctors`

Lista de médicos disponibles (para selects en formularios de cita).

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": [
    { "id": "s4", "name": "Dr. Ricardo Pérez", "specialty": "Cardiología", "status": "activo" },
    { "id": "s5", "name": "Dra. Sofía Blanco", "specialty": "Ginecología", "status": "activo" },
    { "id": "s6", "name": "Dr. Luis Martínez", "specialty": "Medicina General", "status": "inactivo" }
  ]
}
```

> [!NOTE]
> Este endpoint es necesario para poblar el selector de médico en el formulario de `CalendarView` al crear citas. Actualmente está hardcodeado.

---

## 9. Notas Técnicas

### 🔐 Seguridad y Autenticación

| Concepto | Detalle |
|----------|---------|
| **Método de auth** | JWT Bearer Token |
| **Header requerido** | `Authorization: Bearer <token>` |
| **Expiración sugerida** | 8 horas (turno hospitalario) |
| **Refresh token** | Recomendado para evitar re-login |

### 🔒 Permisos por Rol

| Endpoint | superadmin | recepcion | medico |
|----------|:----------:|:---------:|:------:|
| `GET /patients` | ✅ | ✅ | ✅ |
| `POST /patients` | ❌ | ✅ | ❌ |
| `PUT /patients/:id` | ✅ | ✅ | ❌ |
| `GET /appointments` | ✅ (read-only) | ✅ | ✅ (solo sus citas) |
| `POST /appointments` | ❌ | ✅ | ❌ |
| `PATCH /appointments/:id/status` | ❌ | ✅ | ❌ |
| `GET /staff` | ✅ | ❌ | ❌ |
| `POST /staff` | ✅ | ❌ | ❌ |
| `PUT /staff/:id` | ✅ | ❌ | ❌ |
| `DELETE /staff/:id` | ✅ | ❌ | ❌ |
| `PATCH /staff/:id/status` | ✅ | ❌ | ❌ |
| `GET /clinical-history` | ❌ | ❌ | ✅ |
| `POST /clinical-history` | ❌ | ❌ | ✅ |
| `GET /dashboard/superadmin` | ✅ | ❌ | ❌ |
| `GET /dashboard/recepcion` | ❌ | ✅ | ❌ |
| `GET /activity` | ✅ | ❌ | ❌ |
| `GET /doctors` | ❌ | ✅ | ❌ |

### 📐 Formato de respuestas de error

Todas las respuestas de error deben seguir este formato estandarizado:

```json
{
  "success": false,
  "message": "Descripción del error",
  "errors": [
    { "field": "email", "message": "El correo ya está registrado" }
  ]
}
```

| Código HTTP | Uso |
|-------------|-----|
| `200` | Operación exitosa (GET, PUT, PATCH, DELETE) |
| `201` | Recurso creado exitosamente (POST) |
| `400` | Datos inválidos / validación fallida |
| `401` | No autenticado / token inválido |
| `403` | Sin permisos para esa acción |
| `404` | Recurso no encontrado |
| `409` | Conflicto (ej: email duplicado) |
| `500` | Error interno del servidor |

### 🌍 CORS

El backend debe habilitar CORS para los orígenes del frontend:
- `http://localhost:5173` (desarrollo con Vite)
- `https://hav-portal.netlify.app` (producción en Netlify)

### 📅 Formato de Fechas

- **Todas las fechas**: formato ISO `YYYY-MM-DD` (ej: `2026-04-21`)
- **Horas**: formato 24h `HH:mm` (ej: `08:00`, `14:30`)

### 🔧 Variable de Entorno del Frontend

El frontend usará esta variable para conectar al backend:

```env
VITE_API_BASE_URL="https://api.hav.edu.ve/api/v1"
```

---

## 📊 Resumen Total de Endpoints

| # | Método | Endpoint | Descripción |
|---|--------|----------|-------------|
| 1 | `POST` | `/auth/login` | Login |
| 2 | `POST` | `/auth/logout` | Logout |
| 3 | `GET` | `/auth/me` | Perfil del usuario actual |
| 4 | `GET` | `/patients` | Listar pacientes |
| 5 | `GET` | `/patients/:id` | Detalle de paciente |
| 6 | `POST` | `/patients` | Crear paciente |
| 7 | `PUT` | `/patients/:id` | Actualizar paciente |
| 8 | `PUT` | `/patients/:id/vital-signs` | Actualizar signos vitales |
| 9 | `GET` | `/appointments` | Listar citas |
| 10 | `GET` | `/appointments/:id` | Detalle de cita |
| 11 | `POST` | `/appointments` | Crear cita |
| 12 | `PATCH` | `/appointments/:id/status` | Cambiar estado de cita |
| 13 | `DELETE` | `/appointments/:id` | Eliminar cita |
| 14 | `GET` | `/staff` | Listar personal |
| 15 | `POST` | `/staff` | Crear personal |
| 16 | `PUT` | `/staff/:id` | Editar personal |
| 17 | `PATCH` | `/staff/:id/status` | Toggle activo/inactivo |
| 18 | `DELETE` | `/staff/:id` | Eliminar personal |
| 19 | `GET` | `/clinical-history` | Historial clínico por paciente |
| 20 | `POST` | `/clinical-history` | Crear nota SOAP |
| 21 | `PATCH` | `/clinical-history/:id/status` | Cerrar/abrir historia |
| 22 | `GET` | `/dashboard/superadmin` | Stats del superadmin |
| 23 | `GET` | `/dashboard/recepcion` | Stats de recepción |
| 24 | `GET` | `/activity` | Actividad reciente |
| 25 | `GET` | `/doctors` | Lista de médicos |

> **Total: 25 endpoints**
