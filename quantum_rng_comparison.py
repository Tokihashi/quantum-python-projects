import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import random

print("🎲 Квантовый vs Классический генератор случайных чисел")
print("="*60)

# Настройки
NUM_SAMPLES = 1000
DICE_SIDES = 6

def quantum_random_generator(n_samples, max_val):
    n_qubits = int(np.ceil(np.log2(max_val)))
    
    qc = QuantumCircuit(n_qubits, n_qubits)
    for i in range(n_qubits):
        qc.h(i)
    qc.measure_all()
    
    simulator = AerSimulator()
    job = simulator.run(qc, shots=n_samples)
    result = job.result()
    counts = result.get_counts()
    
    outcomes = []
    for binary_str, count in counts.items():
        decimal_val = int(binary_str.replace(' ', ''), 2)
        for _ in range(count):
            outcomes.append((decimal_val % max_val) + 1)
    
    return np.array(outcomes)

def classical_random_generator(n_samples, max_val):
    return np.array([random.randint(1, max_val) for _ in range(n_samples)])

# Запуск
print("⏳ Генерируем данные...")
q_results = quantum_random_generator(NUM_SAMPLES, DICE_SIDES)
c_results = classical_random_generator(NUM_SAMPLES, DICE_SIDES)

# Статистика
print(f"\n📊 Статистика за {NUM_SAMPLES} бросков:\n")
print(f"{'Грань':<8} | {'Квантовый':<12} | {'Классический':<12} | {'Идеал':<8}")
print("-" * 60)

ideal_pct = 100 / DICE_SIDES
q_pcts = []
c_pcts = []

for face in range(1, DICE_SIDES + 1):
    q_pct = np.sum(q_results == face) / NUM_SAMPLES * 100
    c_pct = np.sum(c_results == face) / NUM_SAMPLES * 100
    q_pcts.append(q_pct)
    c_pcts.append(c_pct)
    print(f"{face:<8} | {q_pct:<12.2f}% | {c_pct:<12.2f}% | {ideal_pct:<8.2f}%")

# 📈 ВИЗУАЛИЗАЦИЯ
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# График 1: Сравнение распределений
x = np.arange(1, DICE_SIDES + 1)
width = 0.35

bars1 = axes[0].bar(x - width/2, q_pcts, width, label='Квантовый', color='blue', alpha=0.7)
bars2 = axes[0].bar(x + width/2, c_pcts, width, label='Классический', color='orange', alpha=0.7)
axes[0].axhline(y=ideal_pct, color='red', linestyle='--', label=f'Идеал ({ideal_pct:.2f}%)', linewidth=2)

axes[0].set_xlabel('Грань кубика', fontsize=12)
axes[0].set_ylabel('Частота (%)', fontsize=12)
axes[0].set_title('Сравнение распределений случайных чисел', fontsize=14, fontweight='bold')
axes[0].set_xticks(x)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)
axes[0].set_ylim(0, max(max(q_pcts), max(c_pcts)) * 1.2)

# Добавляем значения на столбцы
for bar in bars1:
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

# График 2: Отклонение от идеала
q_deviation = [abs(p - ideal_pct) for p in q_pcts]
c_deviation = [abs(p - ideal_pct) for p in c_pcts]

axes[1].plot(x, q_deviation, 'b-o', label='Квантовый', linewidth=2, markersize=8)
axes[1].plot(x, c_deviation, 'o--', color='orange', label='Классический', linewidth=2, markersize=8)
axes[1].axhline(y=0, color='red', linestyle='-', linewidth=1, alpha=0.5)

axes[1].set_xlabel('Грань кубика', fontsize=12)
axes[1].set_ylabel('Отклонение от идеала (%)', fontsize=12)
axes[1].set_title('Отклонение от равномерного распределения', fontsize=14, fontweight='bold')
axes[1].set_xticks(x)
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('quantum_rng_comparison.png', dpi=300, bbox_inches='tight')
print("\n✅ График сохранён: quantum_rng_comparison.png")

# Статистические метрики
print("\n📈 СТАТИСТИЧЕСКИЙ АНАЛИЗ:")
q_std = np.std(q_pcts)
c_std = np.std(c_pcts)
print(f"  Стандартное отклонение (квантовый): {q_std:.2f}%")
print(f"  Стандартное отклонение (классический): {c_std:.2f}%")
print(f"  Среднее отклонение (квантовый): {np.mean(q_deviation):.2f}%")
print(f"  Среднее отклонение (классический): {np.mean(c_deviation):.2f}%")

print("\n💡 ВЫВОД:")
if q_std < c_std:
    print("   ✅ Квантовый генератор показал БОЛЕЕ равномерное распределение!")
elif c_std < q_std:
    print("   ✅ Классический генератор показал БОЛЕЕ равномерное распределение!")
else:
    print("   ✅ Оба генератора показали схожие результаты!")

print("\n" + "="*60)
plt.show()