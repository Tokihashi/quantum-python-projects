import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

print("🔐 Квантовая Криптография: Протокол BB84")
print("="*70)

N_BITS = 20

# --- ГЕНЕРАЦИЯ ДАННЫХ ---
alice_bits = np.random.randint(0, 2, N_BITS)
alice_bases = np.random.randint(0, 2, N_BITS)
bob_bases = np.random.randint(0, 2, N_BITS)
eve_bases = np.random.randint(0, 2, N_BITS)

def transmit_bit(a_bit, a_basis, b_basis, e_basis=None, has_eve=False):
    qc = QuantumCircuit(1, 1)
    
    if a_bit == 1:
        qc.x(0)
    if a_basis == 1:
        qc.h(0)
    
    if has_eve:
        if e_basis == 1:
            qc.h(0)
        qc.measure_all()
        
        sim = AerSimulator()
        job = sim.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        eve_result = int(list(counts.keys())[0].replace(' ', ''), 2)
        
        qc = QuantumCircuit(1, 1)
        if eve_result == 1:
            qc.x(0)
        if e_basis == 1:
            qc.h(0)
    
    if b_basis == 1:
        qc.h(0)
    qc.measure_all()
    
    sim = AerSimulator()
    job = sim.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    bob_result = int(list(counts.keys())[0].replace(' ', ''), 2)
    
    return bob_result

# --- ЗАПУСК ---
print("⏳ Симуляция...\n")

bob_safe = [transmit_bit(alice_bits[i], alice_bases[i], bob_bases[i], has_eve=False) 
            for i in range(N_BITS)]
bob_hacked = [transmit_bit(alice_bits[i], alice_bases[i], bob_bases[i], eve_bases[i], has_eve=True) 
              for i in range(N_BITS)]

# --- АНАЛИЗ ---
safe_key = []
hacked_key = []
errors = []
matched_indices = []

for i in range(N_BITS):
    if alice_bases[i] == bob_bases[i]:
        matched_indices.append(i)
        safe_key.append(bob_safe[i])
        hacked_key.append(bob_hacked[i])
        errors.append(1 if bob_hacked[i] != alice_bits[i] else 0)

error_rate = sum(errors) / len(errors) if errors else 0

# --- ВЫВОД ---
print("📊 Результаты (совпавшие базисы):\n")
print(f"{'Бит':<4} | {'Алиса':<7} | {'Боб(чисто)':<11} | {'Боб(с Евой)':<11} | {'Статус'}")
print("-" * 70)

for idx, i in enumerate(matched_indices):
    status = "✅" if errors[idx] == 0 else "🚨 ОШИБКА"
    print(f"{i:<4} | {alice_bits[i]:<7} | {bob_safe[i]:<11} | {bob_hacked[i]:<11} | {status}")

print("\n" + "="*70)
print(f"🔑 Ключ (БЕЗ Евы): {''.join(map(str, safe_key))}")
print(f"🔑 Ключ (С Евой):  {''.join(map(str, hacked_key))}")
print(f"\n📉 Ошибок: {error_rate:.0%}")

if error_rate > 0:
    print("🚨 ОБНАРУЖЕН ПЕРЕХВАТЧИК!")
else:
    print("✅ Канал чист.")

# --- ВИЗУАЛИЗАЦИЯ ---
print("\n📈 Строим графики...")

safe_key_arr = np.array(safe_key)
hacked_key_arr = np.array(hacked_key)
alice_bits_arr = np.array(alice_bits)

fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# ГРАФИК 1: Сравнение ключей
x = np.arange(len(matched_indices))

axes[0].scatter(x, alice_bits_arr[matched_indices], c='blue', label='Алиса (отправила)', s=100, zorder=3)
axes[0].scatter(x, hacked_key_arr, c='red', label='Боб (получил с Евой)', s=100, zorder=3, alpha=0.7)
axes[0].plot(x, alice_bits_arr[matched_indices], 'b-', alpha=0.3)
axes[0].plot(x, hacked_key_arr, 'r--', alpha=0.3)

error_indices = x[np.array(errors) == 1]
if len(error_indices) > 0:
    axes[0].scatter(error_indices, alice_bits_arr[matched_indices][np.array(errors)==1], 
                    c='yellow', edgecolors='black', s=200, zorder=4, marker='X', label='⚠️ Ошибка')

axes[0].set_title('🔐 Квантовый ключ: Алиса → Боб', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Значение бита (0 или 1)')
axes[0].set_xticks(x)
axes[0].set_xticklabels(matched_indices, rotation=45)
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(-0.2, 1.2)
axes[0].set_yticks([0, 1])

# ГРАФИК 2: Статистика
categories = ['Всего битов', 'Совпало базисов', 'Ошибок (Ева)']
values = [N_BITS, len(matched_indices), sum(errors)]
colors = ['lightblue', 'lightgreen', 'red']

bars = axes[1].bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
axes[1].set_title('📊 Итоговая статистика', fontsize=14, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)

for bar, val in zip(bars, values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(val), ha='center', va='bottom', fontsize=12, fontweight='bold')

result_text = f'Ошибок: {sum(errors)} из {len(matched_indices)}\n'
if sum(errors) > 0:
    result_text += '🚨 ЕВА ОБНАРУЖЕНА!'
    box_color = 'lightcoral'
else:
    result_text += '✅ Канал безопасен'
    box_color = 'lightgreen'

axes[1].text(0.5, -1, result_text, ha='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=box_color, alpha=0.8))

plt.tight_layout()
plt.savefig('bb84_final_visualization.png', dpi=300, bbox_inches='tight')
print("✅ Сохранено: bb84_final_visualization.png")

plt.show()