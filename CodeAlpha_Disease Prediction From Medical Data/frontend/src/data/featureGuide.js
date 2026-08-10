export const featureGuide = [
  { key: 'age', label: 'Age', group: 'Patient', unit: 'years', note: 'Age at the time of assessment.', range: '18–100' },
  { key: 'sex', label: 'Sex', group: 'Patient', unit: '', note: 'Sex recorded for the assessment.', range: '0 / 1' },
  { key: 'cp', label: 'Chest pain type', group: 'Symptoms', unit: '', note: "Chest pain category that best matches the patient's presentation.", range: '1–4' },
  { key: 'trestbps', label: 'Resting blood pressure', group: 'Vitals', unit: 'mmHg', note: 'Systolic blood pressure measured at rest.', range: '70–250' },
  { key: 'chol', label: 'Serum cholesterol', group: 'Laboratory', unit: 'mg/dL', note: 'Total serum cholesterol level.', range: '80–700' },
  { key: 'fbs', label: 'Fasting blood sugar', group: 'Laboratory', unit: '', note: 'Whether fasting blood sugar is above 120 mg/dL.', range: '0 / 1' },
  { key: 'restecg', label: 'Resting ECG', group: 'ECG', unit: '', note: 'Resting ECG result category.', range: '0–2' },
  { key: 'thalach', label: 'Maximum heart rate', group: 'Exercise', unit: 'bpm', note: 'Highest heart rate reached during exercise testing.', range: '50–250' },
  { key: 'exang', label: 'Exercise-induced angina', group: 'Exercise', unit: '', note: 'Whether exercise caused angina.', range: '0 / 1' },
  { key: 'oldpeak', label: 'ST depression', group: 'Exercise', unit: 'mm', note: 'Change in the ST segment during exercise compared with rest.', range: '-2.5–10' },
  { key: 'slope', label: 'Peak ST slope', group: 'Exercise', unit: '', note: 'Shape of the ST segment at peak exercise.', range: '1–3' },
  { key: 'ca', label: 'Major vessels', group: 'Imaging', unit: '', note: 'Number of major vessels seen on fluoroscopy.', range: '0–3' },
  { key: 'thal', label: 'Thalassemia test', group: 'Imaging', unit: '', note: 'Thallium stress-test result used by the trained model.', range: '3 / 6 / 7' },
]

export const samplePatient = {
  age: 54, sex: 1, cp: 3, trestbps: 130, chol: 246, fbs: 0, restecg: 0,
  thalach: 150, exang: 0, oldpeak: 1.0, slope: 2, ca: 0, thal: 3,
}
