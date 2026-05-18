import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

print("🔐 Квантовая Криптография: Протокол BB84")
print("="*60)

N_BITS = 8  # Количество битов для передачи (маленькое число для наглядности)

# --- 1. ПОДГОТОВКА ДАННЫХ ---
# 0 = Базис Z (|0>, |1>), 1 = Базис X (|+>, |->)
alice_bits = np.random.randint(0, 2, N_BITS)
alice_bases = np.random.randint(0, 2, N_BITS)
bob_bases = np.random.randint(0, 2, N_BITS)
eve_bases = np.random.randint(0, 2, N_BITS)

# Функция симуляции передачи одного бита
def transmit_bit(a_bit, a_basis, b_basis, e_basis=None, has_eve=False):
    # Создаем цепь из 1 кубита
    qc = QuantumCircuit(1, 1)
    
    # 🟦 ШАГ АЛИСЫ: Подготовка состояния
    if a_bit == 1:
        qc.x(0)  # Бит 1
    if a_basis == 1:
        qc.h(0)  # Перевод в базис X (суперпозиция)
        
    #  ШАГ ЕВЫ (Атака "Intercept-Resend")
    if has_eve:
        # Ева измеряет кубит в своем случайном базисе
        if e_basis == 1:
            qc.h(0)
        qc.measure_all()
        
        # Получаем результат измерения Евы (симуляция)
        sim = AerSimulator()
        job = sim.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        eve_result = int(list(counts.keys())[0].replace(' ', ''), 2)
        
        # Ева отправляет Бобу то, что измерила (пересоздает цепь)
        qc = QuantumCircuit(1, 1)
        if eve_result == 1:
            qc.x(0)
        if e_basis == 1: # Ева отправляет в том базисе, в котором измерила
             qc.h(0)

    #  ШАГ БОБА: Измерение
    if b_basis == 1:
        qc.h(0) # Если базис X, добавляем H перед измерением
    qc.measure_all()
    
    # Запуск симуляции
    sim = AerSimulator()
    job = sim.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    bob_result = int(list(counts.keys())[0].replace(' ', ''), 2)
    
    return bob_result

# --- 2. ЗАПУСК С ЦЕНЗОРОМ И БЕЗ ---
print("⏳ Симуляция передачи ключа...\n")

print(" Сценарий 1: БЕЗ ЕВЫ (Идеальный канал)")
bob_results_safe = []
for i in range(N_BITS):
    res = transmit_bit(alice_bits[i], alice_bases[i], bob_bases[i], has_eve=False)
    bob_results_safe.append(res)

print("🔴 Сценарий 2: С ЕВОЙ (Атака перехватом)")
bob_results_hacked = []
for i in range(N_BITS):
    res = transmit_bit(alice_bits[i], alice_bases[i], bob_bases[i], eve_bases[i], has_eve=True)
    bob_results_hacked.append(res)

# --- 3. СРАВНЕНИЕ И "ПРОСЕИВАНИЕ" (SIFTING) ---
# Мы оставляем только те биты, где Алиса и Боб выбрали одинаковый базис
safe_key = []
hacked_key = []
errors = 0
total_matches = 0

print("\n📊 Таблица результатов (База совпала ✅ / Не совпала ❌):")
print(f"{'Bit':<4} | {'Базис':<6} | {'Алиса':<6} | {'Боб(Без Евы)':<12} | {'Боб(С Евой)':<12}")
print("-" * 75)

for i in range(N_BITS):
    match = (alice_bases[i] == bob_bases[i])
    if match:
        total_matches += 1
        safe_key.append(bob_results_safe[i])
        hacked_key.append(bob_results_hacked[i])
        
        # Считаем ошибки в взломанном канале
        if bob_results_hacked[i] != alice_bits[i]:
            errors += 1
            marker = "⚠️ ОШИБКА"
        else:
            marker = "✅ OK"
    else:
        safe_key.append("-")
        hacked_key.append("-")
        marker = "❌"

    print(f"{i:<4} | {alice_bases[i]:<6} | {alice_bits[i]:<6} | {bob_results_safe[i]:<12} | {bob_results_hacked[i]:<12} {marker}")

# --- 4. ВЕРДИКТ ---
print("\n" + "="*60)
print("🔑 Сформированные ключи (только совпавшие базисы):")
print(f"Алиса: {alice_bits}")
print(f"Боб (Чисто): {safe_key}")
print(f"Боб (Взлом): {hacked_key}")

if total_matches > 0:
    error_rate = errors / total_matches
    print(f"\n📉 Уровень ошибок: {error_rate:.0%}")
    
    if error_rate > 0:
        print("🚨 ВНИМАНИЕ! ОБНАРУЖЕН ПЕРЕХВАТЧИК! (Ева)")
        print("   Квантовая механика не позволяет подслушать без следа.")
        print("   Канал небезопасен. Ключ отброшен.")
    else:
        print("✅ Канал чист. Ключ безопасен.")