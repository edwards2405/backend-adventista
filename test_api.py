import urllib.request
import json

data = json.dumps({"email": "admin@hav.edu.ve", "password": "admin123"}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=data, headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
result = json.loads(response.read())
print(json.dumps(result, indent=2))

token = result['token']

# Crear Paciente
print("\n--- Creando Paciente ---")
patient_data = json.dumps({
  "cedula": "V-12345678",
  "name": "Eduardo San Vicente",
  "gender": "Masculino",
  "phone": "+58 412-555-0101",
  "email": "e.sanvicente@gmail.com",
  "dob": "1979-03-14",
  "bloodType": "O+",
  "insurance": "PDVSA Póliza Oro",
  "status": "activo"
}).encode('utf-8')

req2 = urllib.request.Request('http://localhost:8000/api/v1/patients/', data=patient_data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
try:
    resp2 = urllib.request.urlopen(req2)
    print(json.dumps(json.loads(resp2.read()), indent=2))
except Exception as e:
    print(e.read())

# Crear Cita
print("\n--- Creando Cita ---")
appt_data = json.dumps({
  "patientId": 1,
  "doctor": "Dr. Ricardo Pérez",
  "specialty": "Cardiología",
  "date": "2026-04-25",
  "time": "08:00",
  "type": "Consulta Nueva"
}).encode('utf-8')

req3 = urllib.request.Request('http://localhost:8000/api/v1/appointments/', data=appt_data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
try:
    resp3 = urllib.request.urlopen(req3)
    print(json.dumps(json.loads(resp3.read()), indent=2))
except Exception as e:
    print(e.read())

