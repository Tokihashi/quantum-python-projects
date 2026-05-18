import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

print("⚛️  НАРУШЕНИЕ НЕРАВЕНСТВ БЕЛЛА")
print("="*60)

N_SHOTS = 1000

def bell_experiment(angle_a, angle_b):
    """
    Создаёт запутанные кубиты и измеряет корреляцию
    """
    qc = QuantumCircuit(2, 2)
    
    # 1. Создаём запутанное состояние (Bell pair)
    qc.h(0)           # Суперпозиция первого кубита
    qc.cx(0, 1)       # Запутывание через CNOT
    
    # 2. Поворачиваем кубиты для измерения под разными углами
    qc.ry(angle_a, 0)  # Алиса измеряет под углом angle_a
    qc.ry(angle_b, 1)  # Боб измеряет под углом angle_b
    
    # 3. Измеряем
    qc.measure_all()
    
    # 4. Запускаем симуляцию
    sim = AerSimulator()
    job = sim.run(qc, shots=N_SHOTS)
    result = job.result()
    counts = result.get_counts()
    
    # 5. Считаем корреляцию E(a,b)
    # E = P(одинаковые) - P(разные)
    total = sum(counts.values())
    
    same = 0  # 00 или 11 (коррелированные)
    diff = 0  # 01 или 10 (некоррелированные)
    
    for key, val in counts.items():
        # Qiskit возвращает '00 00', '01 01' и т.д.
        clean_key = key.replace(' ', '')[-2:]
        
        if clean_key in ['00', '11']:
            same += val
        else:
            diff += val
    
    return (same - diff) / total

# Оптимальные углы для НАРУШЕНИЯ неравенства Белла
# (доказано математически)
angle_a = 0
angle_a_prime = np.pi / 2
angle_b = np.pi / 4
angle_b_prime = -np.pi / 4

print("⏳ Проводим 4 измерения...\n")

# Измеряем все 4 комбинации для CHSH неравенства
E_ab = bell_experiment(angle_a, angle_b)
E_ab_prime = bell_experiment(angle_a, angle_b_prime)
E_a_prime_b = bell_experiment(angle_a_prime, angle_b)
E_a_prime_b_prime = bell_experiment(angle_a_prime, angle_b_prime)

print(f"Результаты:")
print(f"  E(a, b)       = {E_ab:.4f}")
print(f"  E(a, b')      = {E_ab_prime:.4f}")
print(f"  E(a', b)      = {E_a_prime_b:.4f}")
print(f"  E(a', b')     = {E_a_prime_b_prime:.4f}")
print()

# CHSH параметр: S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
S = E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime

print("="*60)
print(f"ПАРАМЕТР CHSH: S = {S:.4f}")
print()
print("ГРАНИЦЫ:")
print(f"  Классический мир (локальный реализм): |S| ≤ 2")
print(f"  Квантовый мир:                        |S| ≤ 2.828")
print()

if abs(S) > 2:
    print(f"🎉 НЕРАВЕНСТВО БЕЛЛА НАРУШЕНО!")
    print(f"   |S| = {abs(S):.4f} > 2")
    print()
    print("✅ ЧТО ЭТО ЗНАЧИТ:")
    print("   • Частицы НЕ имеют предопределённых свойств до измерения")
    print("   • Квантовая запутанность — реальное физическое явление")
    print("   • Измерение одной частицы мгновенно влияет на другую")
    print("   • Локальный реализм (классическая логика) НЕВЕРЕН")
    print()
    print("🏆 За это открытие дали Нобелевскую премию 2022 года!")
else:
    print(f"⚠️  S = {S:.4f} (не нарушено или на границе)")
    print("   Попробуй увеличить N_SHOTS для точности")

print("\n" + "="*60)