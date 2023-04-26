#!/usr/bin/env python
# coding: utf-8

# # Circuit Boxes in pytket
# 
# Quantum algorithms are often described at the level of individual logic gates. Thinking of quantum circuits in this way can have some benefits as quantum device performance is still influenced by low level implementation details.
# 
# However quantum circuits can be challenging to interpret if expressed in terms of primtive gates only. This motivates the idea of circuit boxes which contain circuits performing a subroutine in a quantum algorithm.

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


# ## Controlled Unitary Operations with `QControlBox`

# TKET also supports the use of "Controlled-U" operations where U is some unitary box defined by the user.
# 
# This can be done by defining a `QControlBox`. These controlled operations can be made from a `CircBox` or any other box type in TKET that doesn't contain classical operations.

# Lets define a multicontrolled $\sqrt{Z}$ gate using the `Unitary1qBox` that we defined above.

# In[9]:


from pytket.circuit import QControlBox

# sqrt(Z) gate controlled on two qubits 
c2_rootz = QControlBox(u1_box, n=2)

test_circ2 = Circuit(3).X(0).CX(0, 1)
test_circ2.add_qcontrolbox(c2_rootz, [0, 1, 2])

render_circuit_jupyter(test_circ2)


# ## Phase Polynomials and Pauli Exponentials

# In[11]:


from pytket import Qubit
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
# U_P = e^{i \theta P}\,, \quad \theta \in \mathbb{R}, \,\,P \in \{I,\, X,\, Y,\, Z \}
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
# U_{XYYZ} = e^{i \theta XYYZ}\,, \quad U_{ZZYX} = e^{i \theta ZZYX}
# \end{equation}
# $$
# 
# We can implement these two Pauli exponetials using the `PauliExpBox` in pytket.
# 
# 

# In[12]:


from pytket.circuit import PauliExpBox
from pytket.pauli import Pauli, QubitPauliString

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

# In the context of quantum circuits a multiplexor is type of generalised multicontrolled gate. 

# In[25]:


from pytket.circuit import Op, MultiplexorBox


op_map = {(0, 0): Op.create(OpType.Rz, 0.3), (1, 1): Op.create(OpType.H)}
multiplexor = MultiplexorBox(op_map)


mutli_circ = Circuit(3).add_multiplexor(multiplexor, [Qubit(0), Qubit(1), Qubit(2)])


# In[ ]:





# $$
# \begin{equation}
# |\psi \rangle = \sqrt{p} |00\rangle + \sqrt{1-p} |11 \rangle
# \end{equation}
# $$

# In[21]:


prob = 0.4

prob_state = np.array([np.sqrt(prob), 0, 0,  np.sqrt(1 - prob)])


# In[22]:


prob_state


# In[23]:


from pytket.circuit import StatePreparationBox

prob_state_box = StatePreparationBox(prob_state)

circ = Circuit(2)
circ.add_state_preparation_box(prob_state_box, [Qubit(0), Qubit(1)])


# In[24]:


render_circuit_jupyter(circ)

