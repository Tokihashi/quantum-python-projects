import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorEstimator  # ✅ Изменено
from qiskit.circuit.library import TwoLocal

print("🔹 Запуск VQE...")

hamiltonian = SparsePauliOp.from_list([
    ("ZI", 0.5), ("IZ", 0.5), ("XX", 0.25)
])

ansatz = TwoLocal(hamiltonian.num_qubits, ["ry", "rz"], "cz", reps=3)  
optimizer = COBYLA(maxiter=200)
estimator = StatevectorEstimator()  # ✅ Изменено

vqe = VQE(estimator, ansatz, optimizer)
result = vqe.compute_minimum_eigenvalue(hamiltonian)

print(f"✅ Энергия: {result.eigenvalue.real:.6f}")
