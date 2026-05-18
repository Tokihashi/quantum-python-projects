import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import random

print("🎲 Квантовый vs Классический генератор случайных чисел")
print("="*50)

# Настройки
NUM_SAMPLES = 1000
DICE_SIDES = 6

# ---------------------------------------------------------
# 🔵 КВАНТОВЫЙ ГЕНЕРАТОР
# ---------------------------------------------------------
def quantum_random_generator(n_samples, max_val):
    n_qubits = int(np.ceil(np.log2(max_val)))
    
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Суперпозиция
    for i in range(n_qubits):
        qc.h(i)
    
    # Измерение
    qc.measure_all()
    
    # Симуляция
    simulator = AerSimulator()
    job = simulator.run(qc, shots=n_samples)
    result = job.result()
    counts = result.get_counts()
    
    # Обработка результатов
    outcomes = []
    for binary_str, count in counts.items():
        decimal_val = int(binary_str.replace(' ', ''), 2)
        for _ in range(count):
            outcomes.append((decimal_val % max_val) + 1)
    
    return np.array(outcomes)

# ---------------------------------------------------------
# 🟠 КЛАССИЧЕСКИЙ ГЕНЕРАТОР
# ---------------------------------------------------------
def classical_random_generator(n_samples, max_val):
    return np.array([random.randint(1, max_val) for _ in range(n_samples)])

# ---------------------------------------------------------
# 🚀 ЗАПУСК
# ---------------------------------------------------------
print("⏳ Генерируем данные...")
q_results = quantum_random_generator(NUM_SAMPLES, DICE_SIDES)
c_results = classical_random_generator(NUM_SAMPLES, DICE_SIDES)

print(f"\n Статистика за {NUM_SAMPLES} бросков (кубик 1-{DICE_SIDES}):")
print(f"{'Грань':<6} | {'Квантовый':<10} | {'Классический':<12} | {'Идеал'}")
print("-" * 50)

ideal_pct = 100 / DICE_SIDES
for face in range(1, DICE_SIDES + 1):
    q_pct = np.sum(q_results == face) / NUM_SAMPLES * 100
    c_pct = np.sum(c_results == face) / NUM_SAMPLES * 100
    print(f"{face:<6} | {q_pct:<10.2f}% | {c_pct:<12.2f}% | {ideal_pct:.2f}%")

print("\n🔍 Вывод:")
print("✅ Оба метода работают!")