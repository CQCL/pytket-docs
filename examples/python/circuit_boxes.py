#!/usr/bin/env python
# coding: utf-8

# # Circuit Boxes in pytket
# 
# Quantum algorithms are often described at the level of individual logic gates. Thinking of quantum circuits in this way can have some benefits as quantum device performance is greatly influenced by low level implementation details such as gate count and circuit depth.
# 
# However quantum circuits can be challenging to interpret if expressed in terms of primtive gates only. This motivates the idea of circuit boxes which contain circuits performing higher level subroutines.

# As a minimal example lets build a circuit to prepare a GHZ state and wrap it up in a `CircBox`.

# In[1]:


from pytket.circuit import Circuit, CircBox
from pytket.circuit.display import render_circuit_jupyter

ghz_circ = Circuit(3, name='GHZ')
ghz_circ.H(0).CX(0, 1).CX(0, 2)

ghz_box = CircBox(ghz_circ) # Construct a CircBox from Circuit

test_circ = Circuit(3)
test_circ.X(0).X(1)
test_circ.CCX(0, 1, 2)

test_circ.add_circbox(ghz_box, [0, 1, 2]) # Add Circbox to Circuit

render_circuit_jupyter(test_circ) # Draw interactive diagram


# Notice how the `CircBox` inherits the name "GHZ" from the underlying circuit and appears in the circuit diagram. We can also inspect the underlying `Circuit` by clicking on the box in the circuit display.

# ## The Quantum Fourier Transform subroutine

# The quantum fourier transform (QFT) is a widely used subroutine in quantum computing appearing in Shor's algorithm and phase estimation based approaches to quantum chemistry.

# We can build the circuit for the $n$ qubit QFT using $n$ Hadamard gates $\frac{n}{2}$ swap gates and $\frac{n(n-1)}{2}$ controlled unitary rotations.  
# 
# $$
# \begin{equation}
# \text{CU1} = 
# \begin{pmatrix}
# I & 0 \\
# 0 & \text{U1}
# \end{pmatrix}
# \,, \quad 
# \text{U1} = 
# \begin{pmatrix}
# 1 & 0 \\
# 0 & e^{i \pi \theta}
# \end{pmatrix}
# \end{equation}
# $$
# 
# We will rotate by smaller and smaller angles of $\theta = \frac{1}{2^{n-1}}$ 

# Lets build the QFT circuit for 3 qubits.

# In[2]:


from pytket.circuit import OpType

qft_circ = Circuit(3, name="QFT")

qft_circ.H(0)
qft_circ.add_gate(OpType.CU1 , [0.5], [1, 0])
qft_circ.add_gate(OpType.CU1 , [0.25], [2, 0])

qft_circ.H(1)
qft_circ.add_gate(OpType.CU1 , [0.5], [2, 1])

qft_circ.H(2)

qft_circ.SWAP(0, 2)

render_circuit_jupyter(qft_circ)


# In[3]:


qft3_box = CircBox(qft_circ) # Define QFT box


# The inverse quantum fourier transform is also a very common subroutine. We can make a `CircBox` for doing the inverse transformation easily using `CircBox.dagger`. 

# In[4]:


qft3_inv_box = qft3_box.dagger


# We can inspect the underlying circuit with the `CircBox.get_circuit()` method.

# In[5]:


qft3_inv = qft3_inv_box.get_circuit()

render_circuit_jupyter(qft3_inv)


# In[6]:


qft3_box = CircBox(qft_circ)

circ = Circuit(3).X(0).CX(0, 1).CX(0, 2)

circ.add_circbox(qft3_box, [0, 1, 2])

render_circuit_jupyter(circ)


# ## Boxes for Unitary Synthesis
# 
# A useful feature when constructing circuits is the ability to generate a circuit to implement a given unitary transformation. This is useful when the disired unitary cannot be expressed directly as a single gate operation. 

# Unitary synthesis is supported in pytket for 1, 2 and 3 qubit unitaries using the `Unitary1qBox`, `Unitary2qBox` and `Unitary3qBox`.

# As an example lets synthesise circuits to implement the $\sqrt{Z}$ and Fermionic SWAP (FSWAP) operations which correspond to the following two unitaries.
# 
# $$
# \begin{equation}
# \sqrt{Z} = 
# \begin{pmatrix}
# 1 & 0 \\
# 0 & i \\
# \end{pmatrix}
# \, , \quad
# \text{FSWAP} =
# \begin{pmatrix}
# 1 & 0 & 0 & 0 \\
# 0 & 0 & 1 & 0 \\
# 0 & 1 & 0 & 0\\
# 0 & 0 & 0 & -1 
# \end{pmatrix}
# \end{equation}
# $$
# 
# We can simply construct a `Unitary2qBox` from a numpy array.

# In[7]:


from pytket.circuit import Unitary1qBox, Unitary2qBox
import numpy as np

unitary_1q = np.asarray([
                 [1, 0],
                 [0, 1j]])

u1_box = Unitary1qBox(unitary_1q)

unitary_2q = np.asarray([
                 [1, 0, 0, 0],
                 [0, 0, 1, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, -1]])

u2_box = Unitary2qBox(unitary_2q)

test_circ = Circuit(2)
test_circ.add_unitary1qbox(u1_box, 0)
test_circ.add_unitary2qbox(u2_box, 0, 1)

render_circuit_jupyter(test_circ)


# Internally unitary boxes expressses the unitary operation in terms of gates supported by pytket. We can view the underlying circuirt with the `CircBox.get_circuit()` method or by applying the `DecomposeBoxes` compilation pass.

# In[8]:


render_circuit_jupyter(u2_box.get_circuit())


# Synthesising a circuit for a general unitary is only supported in pytket for up to 3 qubits. This is because unitary synthesis scales poorly with respect to both runtime and circuit complexity.
# 
# However for special cases unitary synthesis becomes an easier problem. The `DiagonalBox` allows the user to synthesise circuits for diagoanl unitaries. Here the `DiagonalBox` can be constructed using a numpy array of the diagonal elements rather than the entire unitary.
# 
# As an example let's synthesise a circuit for the following 4 qubit diagoanl unitary.
# 
# $$
# \begin{equation}
# U_{4q} = \text{diag}(1, i, 1, i, 1, i, 1, i, 1, i, 1, i, 1, i, 1, i)
# \end{equation}
# $$

# In[9]:


from pytket.circuit import Qubit, DiagonalBox

diagonal_4q = [1, 1j] * 8
diag_box = DiagonalBox(diagonal_4q)

circ_4q = Circuit(4)
circ_4q.add_diagonal_box(diag_box, [Qubit(i) for i in range(circ_4q.n_qubits)])

render_circuit_jupyter(circ_4q)


# The `DiagonalBox` will be constructed using a sequence of `Mutliplexor` operations - more on these later.

# ## Controlled Unitary Operations with `QControlBox`

# TKET also supports the use of "Controlled-U" operations where U is some unitary box defined by the user.
# 
# This can be done by defining a `QControlBox`. These controlled operations can be made from a `CircBox` or any other box type in TKET that doesn't contain classical operations.

# Lets define a multicontrolled $\sqrt{Z}$ gate using the `Unitary1qBox` that we defined above.

# In[10]:


from pytket.circuit import QControlBox

# sqrt(Z) gate controlled on two qubits 
c2_rootz = QControlBox(u1_box, n=2)

test_circ2 = Circuit(3).X(0).CX(0, 1)
test_circ2.add_qcontrolbox(c2_rootz, [0, 1, 2])

render_circuit_jupyter(test_circ2)


# ## Phase Polynomials and Pauli Exponentials

# In[11]:


from pytket.circuit import PhasePolyBox

c = Circuit(3)

n_qb = 3

qubit_indices = {Qubit(0): 0, Qubit(1): 1, Qubit(2): 2}

phase_polynomial = {
        (True, False, True): 0.333,
        (False, False, True): 0.05,
        (False, True, False): 1.05,}

linear_transformation = np.array([[1, 1, 0], [0, 1, 0], [0, 0, 1]])

p_box = PhasePolyBox(n_qb,
                     qubit_indices,
                     phase_polynomial,
                     linear_transformation)

c.add_phasepolybox(p_box, [0, 1, 2])

render_circuit_jupyter(p_box.get_circuit())


# Exponentiated Pauli operators appear in many applications of quantum computing. 
# 
# Pauli exponentials are defined in terms of a Pauli string $P$ and a phase $\theta$ and are written in the following form
# 
# $$
# \begin{equation}
# U_P = e^{i \frac{\theta}{2} P}\,, \quad \theta \in \mathbb{R}, \,\,P \in \{I,\, X,\, Y,\, Z \}
# \end{equation}
# $$
# 
# 
# Pauli strings are tensor products of the Pauli matrices $\{I,\, X,\, Y,\, Z \}$
# 
# 
# $$
# \begin{equation}
# XYYZ \equiv X \otimes Y \otimes Y \otimes Z
# \end{equation}
# $$
# 
# Consider the following two Pauli Exponentials
# 
# $$
# \begin{equation}
# U_{XYYZ} = e^{i \frac{\theta}{2} XYYZ}\,, \quad U_{ZZYX} = e^{i \frac{\theta}{2} ZZYX}
# \end{equation}
# $$
# 
# We can implement these two Pauli exponetials using the `PauliExpBox` in pytket.
# 
# 

# In[12]:


from pytket.circuit import PauliExpBox
from pytket.pauli import Pauli

# Construct PauliExpBox(es) with a list of Paulis followed by the phase
xyyz = PauliExpBox([Pauli.X, Pauli.Y, Pauli.Y, Pauli.Z], -0.2)
zzyx = PauliExpBox([Pauli.Z, Pauli.Z, Pauli.Y, Pauli.X], 0.7)

pauli_circ = Circuit(5)

pauli_circ.add_pauliexpbox(xyyz, [0, 1, 2, 3])
pauli_circ.add_pauliexpbox(zzyx, [1, 2, 3, 4])

render_circuit_jupyter(pauli_circ)


# To understand what happens inside a `PauliExpBox` lets take a look at the underlying circuit for $e^{i\theta \text{ZZYX}}$.

# In[13]:


render_circuit_jupyter(zzyx.get_circuit())


# All Pauli Exponetials of the form above can be implemented in terms of a single Rz($\theta$) rotation and a symmetric chain of CX gates on either side together with some single qubit basis rotations. This class of circuit is called a Pauli Gadget. The subset of these circuits corresponding to "Z only" Pauli strings are referred to as phase gadgets.
# 
# We see that the Pauli exponential $e^{i\theta \text{ZZYX}}$ has basis rotations on the third and fourth qubit. The V and Vdg gates rotate from the default Z basis to the Y basis and the Hadamard gate serves to change to the X basis.
# 
# These Pauli gadget circuits have interesting algebraic properties which are useful for circuit optimisation. For further discussion see the research publication on phase gadget synthesis ( 	arXiv:1906.01734). Ideas from this paper are implemented in TKET as the `OptimisePhaseGadgets` and `PauliSimp` optimisation passes.

# ## Multiplexors, State Preperation and ToffoliBox

# In the context of quantum circuits a multiplexor is type of generalised multicontrolled gate. Multiplexors grant us the flexibilty to specify different operations on target qubits for different control states.
# 
# To create a multiplexor we simply construct a dictionary where the keys are the state of the control qubits and the values represent the operation perfomed on the target.
# 
# Lets implement a multiplexor with the following logic. Here we treat the first two qubits a controls and the third qubit as the target.
# 
# ```
# input state |000>
# 
# if control qubits in |00>:
#     do Rz(0.3) on third qubit
# else if control qubits in |11>:
#      do H on third qubit
# else:
#     do identity (aka do nothing)
# ```

# In[14]:


from pytket.circuit import Op, MultiplexorBox

# Define both gates as an Op
rz_op = Op.create(OpType.Rz, 0.3)
h_op = Op.create(OpType.H)

op_map = {(0, 0): rz_op, (1, 1): h_op}
multiplexor = MultiplexorBox(op_map)


# In[15]:


# Assume all qubits initialised to |0> here
multi_circ = Circuit(3)
multi_circ.X(0).X(1) # Put both control qubits in the state |1>
multi_circ.add_multiplexor(multiplexor, [Qubit(0), Qubit(1), Qubit(2)])

render_circuit_jupyter(multi_circ)


# Notice how in the example above the control qubits are both in the $|1\rangle$ state and so the multiplexor applies the Hadamard operation to the third qubit. If we calculate our statevector we see that the third qubit is in the $|+\rangle = H|0\rangle$ state.

# In[16]:


print("Statevector =", multi_circ.get_statevector()) # amplitudes of |+> approx 0.707...


# One place where multiplexor operations are useful is in state preperation algorithms. 
# 
# TKET supports the preperation of arbitrary quantum states via the `StatePreparationBox`. This box takes a $ (1\times 2^n)$ numpy array representing the $n$ qubit statevector where the entries represent the amplitudes of the quantum state.
# 
# Given the vector of amplitudes TKET will construct a box containing a sequence of multiplexors using the method outlined in (arXiv:quant-ph/0406176).
# 
# Note that generic state preperation circuits can be very complex with the gatecount and depth increasing rapidly with the size of the state. For statevectors with only real amplitudes only multiplexed Ry is needed to accomplish the state prepartion.   
# 
# Lets prepare the following quantum state encoding the binomial distribution. Here $p$ is a probability so the state is always normalised.
# 

# $$
# \begin{equation}
# |\psi \rangle = \sqrt{p} |00\rangle + \sqrt{1-p} |11 \rangle\,, \quad p \in [0, 1]
# \end{equation}
# $$

# In[17]:


prob = 0.4 # Pick a value of p

prob_state = np.array([np.sqrt(prob), 0, 0,  np.sqrt(1 - prob)]) # Statevector array


# In[18]:


np.round(prob_state, 3)


# In[19]:


from pytket.circuit import StatePreparationBox

prob_state_box = StatePreparationBox(prob_state)

state_circ = Circuit(2)
state_circ.add_state_preparation_box(prob_state_box, [Qubit(0), Qubit(1)])
render_circuit_jupyter(state_circ)


# In[20]:


# Verify state preperation
np.round(state_circ.get_statevector().real, 3) 


# Finally lets consider another box type namely the `ToffoliBox`. This box can be used to prepare an arbitary permutation of the computational basis states.
# 
# To construct the box we need to specify the permuation as a key:value pair where the key is the input basis state and the value is output. 
# 
# Lets construct a `ToffoliBox` to perform the following mapping
# 
# $$
# \begin{equation}
# |001\rangle \longmapsto |111\rangle \\
# |111\rangle \longmapsto |001\rangle
# \end{equation}
# $$
# 
# For consistency if a basis state appears as key in the permutation dictionary then it must also appear and a value.

# In[21]:


from pytket.circuit import ToffoliBox

# Specify the desired permutation of the basis states
mapping = {(0, 0, 1): (1, 1, 1), (1, 1, 1): (0, 0, 1)}

# Define box to perform the permutation
perm_box = ToffoliBox(permutation=mapping)

circ = Circuit(3)
circ.X(2)
circ.add_toffolibox(perm_box, [0, 1, 2]) 
render_circuit_jupyter(circ)


# In[22]:


np.round(circ.get_statevector().real, 3) #|001> input -> |111> output 


# The permutation is implemented using a sequence of multiplexed rotations followed by a `DiagonalBox`.

# In[23]:


render_circuit_jupyter(perm_box.get_circuit())

