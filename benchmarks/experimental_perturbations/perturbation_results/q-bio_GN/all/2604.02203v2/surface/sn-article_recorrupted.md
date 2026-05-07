%Version 3.1 December 2024
% See section 11 of the User Manual for version history
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%                                                                 %%
%% Please do not use \input{...} to include other tex files.       %%
%% Submit your LaTeX manuscript as one .tex document.              %%
%%                                                                 %%
%% All additional figures and files should be attached             %%
%% separately and not embedded in the \TeX\ document itself.       %%
%%                                                                 %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%\documentclass[referee,sn-basic]{sn-jnl}% referee option is meant for double line spacing

%%=======================================================%%
%% to print line numbers in the margin use lineno option %%
%%=======================================================%%

%%\documentclass[lineno,pdflatex,sn-basic]{sn-jnl}% Basic Springer Nature Reference Style/Chemistry Reference Style

%%=========================================================================================%%
%% the documentclass is set to pdflatex as default. You can delete it if not appropriate.  %%
%%=========================================================================================%%

%%\documentclass[sn-basic]{sn-jnl}% Basic Springer Nature Reference Style/Chemistry Reference Style

%%Note: the following reference styles support Namedate and Numbered referencing. By default the style follows the most common style. To switch between the options you can add or remove Numbered in the optional parenthesis. 
%%The option is available for: sn-basic.bst, sn-chicago.bst%  
 
%%\documentclass[pdflatex,sn-nature]{sn-jnl}% Style for submissions to Nature Portfolio journals
%%\documentclass[pdflatex,sn-basic]{sn-jnl}% Basic Springer Nature Reference Style/Chemistry Reference Style
\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}% Math and Physical Sciences Numbered Reference Style
%%\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}% Math and Physical Sciences Author Year Reference Style
%%\documentclass[pdflatex,sn-aps]{sn-jnl}% American Physical Society (APS) Reference Style
%%\documentclass[pdflatex,sn-vancouver-num]{sn-jnl}% Vancouver Numbered Reference Style
%%\documentclass[pdflatex,sn-vancouver-ay]{sn-jnl}% Vancouver Author Year Reference Style
%%\documentclass[pdflatex,sn-apa]{sn-jnl}% APA Reference Style
%%\documentclass[pdflatex,sn-chicago]{sn-jnl}% Chicago-based Humanities Reference Style

%%%% Standard Packages
%%<additional latex packages if required can be included here>
\usepackage{graphicx}%
\usepackage{multirow}%
\usepackage{amsmath,amssymb,amsfonts}%
\usepackage{amsthm}%
\usepackage{mathrsfs}%
\usepackage[title]{appendix}%
\usepackage{xcolor}%
\usepackage{textcomp}%
\usepackage{manyfoot}%
\usepackage{booktabs}%
\usepackage{algorithm}%
\usepackage{algorithmicx}%
\usepackage{algpseudocode}%
\usepackage{listings}%
\usepackage{braket}
\usepackage{float}
%%%%

%%%%%=============================================================================%%%%
%%%%  Remarks: This template is provided to aid authors with the preparation
%%%%  of original research articles intended for submission to journals published 
%%%%  by Springer Nature. The guidance has been prepared in partnership with 
%%%%  production teams to conform to Springer Nature technical requirements. 
%%%%  Editorial and presentation requirements differ among journal portfolios and 
%%%%  research disciplines. You may find sections in this template are irrelevant 
%%%%  to your work and are empowered to omit any such section if allowed by the 
%%%%  journal you intend to submit to. The submission guidelines and policies 
%%%%  of the journal take precedence. A detailed User Manual is available in the 
%%%%  template package for technical guidance.
%%%%%=============================================================================%%%%

%% as per the requirement new theorem styles can be included as shown below
\theoremstyle{thmstyleone}%
\newtheorem{theorem}{Theorem}%  meant for continuous numbers
%%\newtheorem{theorem}{Theorem}[section]% meant for sectionwise numbers
%% optional argument [theorem] produces theorem numbering sequence instead of independent numbers for Proposition
\newtheorem{proposition}[theorem]{Proposition}% 
%%\newtheorem{proposition}{Proposition}% to get separate numbers for theorem and proposition etc.

\theoremstyle{thmstyletwo}%
\newtheorem{example}{Example}%
\newtheorem{remark}{Remark}%

\theoremstyle{thmstylethree}%
\newtheorem{definition}{Definition}%

\raggedbottom
%%\unnumbered% uncomment this for unnumbered level heads

\begin{document}

\title[Article Title]{QuantumXCT: Learning Interaction-Induced State Transformation in Cell-Cell Communication via Quantum Entanglement and Generative Modeling}

%%=============================================================%%
%% GivenName	-> \fnm{Joergen W.}
%% Particle	-> \spfx{van der} -> surname prefix
%% FamilyName	-> \sur{Ploeg}
%% Suffix	-> \sfx{IV}
%% \author*[1,2]{\fnm{Joergen W.} \spfx{van der} \sur{Ploeg} 
%%  \sfx{IV}}\email{iauthor@gmail.com}
%%=============================================================%%

\author*[1,2,3]{\fnm{Selim} \sur{Romero}}\email{ssromerogon@tamu.edu}

\author[1,3]{\fnm{Shreyan} \sur{Gupta}}\email{xenon8778@tamu.edu}

\author[2,3]{\fnm{Robert S.} \sur{Chapkin}}\email{r-chapkin@tamu.edu}

\author*[1,3,4]{\fnm{James J.} \sur{Cai}}\email{jcai@tamu.edu}

\affil[1]{\orgdiv{Department of Veterinary Integrative Biosciences}, \orgname{Texas A\&M University}} 

\affil[2]{\orgdiv{Department of Nutrition}, \orgname{Texas A\&M University}}

\affil[3]{\orgdiv{CPRIT Single Cell Data Science Core}, \orgname{Texas A\&M University}}

\affil[4]{\orgdiv{Department of Electrical and Computer Engineering}, \orgname{Texas A\&M University}}

%%==================================%%
%% Sample for unstructured abstract %%
%%==================================%%

\abstract{Inferring cell–cell communication (CCC) from single-cell transcriptomics remains fundamentally limited by reliance on curated ligand–receptor databases, which primarily capture co-expression rather than the system-level effects of signaling on cellular states. Here, we introduce QuantumXCT, a hybrid quantum–classical generative framework that reframes CCC as a problem of learning interaction-induced state transformations between cellular state distributions. By encoding transcriptomic profiles into a high-dimensional Hilbert space, QuantumXCT trains parameterized quantum circuits to learn a unitary transformation that maps a baseline non-interacting cellular state to an interacting state. This approach enables the discovery of communication-driven changes in cellular state distributions without requiring prior biological assumptions. We validate QuantumXCT using both synthetic data with known ground-truth interactions and single-cell RNA-seq data from ovarian cancer–fibroblast co-culture model. The QuantumXCT model accurately recovered complex regulatory dependencies, including feedback structures, and identified dominant communication hubs such as the \texttt{PDGFB-PDGFRB-STAT3} axis. Importantly, the learned quantum circuit is interpretable: its entangling topology was translated into biologically meaningful interaction networks, while post hoc contribution analysis quantified the relative influence of individual interactions on the observed state transitions. Notably, by shifting CCC inference from static interaction lookup to learning data-driven state transformations, QuantumXCT provides a generative framework for modeling intercellular communication. This work establishes a new paradigm for \textit{de novo} discovery of communication programs in complex biological systems and highlights the potential of quantum machine learning in the context of single-cell biology.
}

%%================================%%
%% Sample for structured abstract %%
%%================================%%
% \abstract{\textbf{Purpose:} 
% 
% \textbf{Methods:} 
% 
% \textbf{Results:}
% 
% \textbf{Conclusion:} }

\keywords{Quantum Computing, Quantum Machine Learning, Bioinformatics, Single-cell}

\maketitle

\section{Introduction}\label{sec_intro}
Inferring cell-cell communication (CCC) from single-cell transcriptomic data is challenging but crucial for understanding complex biological systems. Over the past decade, a growing ecosystem of computational tools has emerged to address this problem, ranging from ligand-receptor scoring methods such as CellChat \cite{jin2021inference, jin2025cellchat} and CellPhoneDB \cite{efremova2020cellphonedb} to multi-method frameworks such as LIANA \cite{dimitrov2022comparison} and semi-supervised approaches such as scTenifoldXct \cite{yang2023sctenifoldxct}. Despite this diversity, most current methods remain tethered to curated databases of known ligand-receptor pairs \cite{armingol2024diversification}. This reliance creates a critical bottleneck: it constrains discovery to existing knowledge and limits the identification of novel or context-specific signaling pathways. A systematic comparison of sixteen inference resources and seven methods showed that both resource and method selection strongly influence predicted interactions, underscoring the instability of database-dependent approaches \cite{dimitrov2022comparison}. Moreover, as we have recently demonstrated in a simulation study  \cite{romero2025qsimcells}, standard CCC inference methods fail to recover programmed causal pathways and instead report spurious associations driven by expression statistics alone. At their core, existing methods are primarily designed to test co-expression of known interacting genes rather than learn the underlying principles of communication directly from the data \cite{armingol2024diversification}.

To overcome these limitations, we propose a paradigm shift in CCC inference. Rather than searching for interacting ligand-receptor pairs, we treat CCC inference as a problem modeling the emergent transformation of cellular states induced by interaction. Specifically, we hypothesize that the communication signal is quantitatively captured by the difference between two transcriptomic probability distributions: a baseline state of cells in isolation (e.g., mono-culture) and a perturbed state measured in an interacting context (e.g., co-culture). Defining this high-dimensional distributional shift---without imposing prior biological assumptions---requires a new class of computational modeling.

While classically intractable, this task is well suited to the strengths of quantum computing. Quantum systems are inherently probabilistic and excel at representing the complex, high-dimensional probability landscapes that are difficult to capture with classical computers. A quantum processor with $n$ qubits can naturally explore a state space of $n^2$ dimensions, mirroring the possibly immense combinatorial complexity of a cell's transcriptome. Leveraging superposition and entanglement, a parameterized quantum circuit (PQC) \cite{benedetti2019parameterized} can be trained to approximate intricate probability distributions, making it a promising tool for capturing subtle, system-wide shifts induced by cell-cell interactions. This capability is harnessed within a hybrid quantum-classical optimization loop \cite{cerezo2021variational}, in which a classical optimizer iteratively refines the quantum circuit's parameters to minimize a data-driven cost function.

Crucially, the trained PQC is not a black box; it provides an interpretable model of the underlying dynamics. The optimized parameters of the learned unitary transformation encapsulate the rules governing cellular state changes, reflecting both intercellular signaling and downstream intracellular responses, such as gene regulatory network (GRN) rewiring. By learning the transformation itself, our quantum machine learning (QML) approach yields a data-driven representation of interactions. Moreover, by comparing circuits optimized under different biological conditions, we can systematically identify how communication programs are altered across development or disease.

To achieve this, we introduce a novel, database-free hybrid quantum-classical framework for learning CCC dynamics. Our approach centers on training a PQC to function as a \textit{generative transformation model}. Rather than adopting a standard classification-oriented Quantum Neural Network (QNN) architecture, we pioneer a method where the circuit learns to execute the unitary transformation that evolves a non-interacting cellular state into an interacting one. The optimization of the circuit's entangling topology and its gate parameters is guided by a custom-designed cost function based on the Kullback-Leibler (KL) divergence, which minimizes the difference between the circuit's output distribution and the empirically observed interacting cells' data (Fig.~\ref{fig:scheme}). We demonstrate this methodology on single-cell RNA sequencing (scRNA-seq) data, establishing a new avenue for the \textit{de novo} discovery of cellular communication channels.

\begin{figure}[h!]
    \centering
    \includegraphics[width=\textwidth]{Fig1_scheme.pdf}
    
    \caption{\textbf{A Quantum Generative Framework for Modeling Cell-Cell Communication.} 
    Our workflow reframes CCC as a learned transformation between cellular states. We derive two sets of empirical probability distributions from single-cell RNA sequencing: a \textbf{baseline distribution}, $P(X^{\text{Mo}})$, from non-interacting (mono-culture) cells, and a \textbf{target distribution}, $Q(X^{\text{Mo}})$, from interacting (co-culture) cells. A parameterized quantum circuit (PQC) is then trained to model this transformation. The circuit is initialized to the global baseline state $\ket{\Psi_{\text{Mo}}}$ (derived from $P(X^{\text{Mo}})$) and applies a parameterized unitary operator, $U(\tau + \theta)$, to produce a final state whose simulated marginal distributions are denoted $P_{\psi'}$. In a hybrid quantum-classical loop, an optimizer iteratively adjusts the circuit's topology ($\theta$) and parameters ($\theta$) to minimize the Kullback-Leibler (KL) divergence, $D_{\text{KL}}(P_{\psi'} \parallel Q_{\text{Co}})$, between the circuit's simulated output and the empirical target. Upon convergence, the optimized unitary, $U(\tau_{\text{opt}}, \theta_{\text{opt}})$, provides a quantitative, data-driven model of the communication dynamics.
    }
    \label{fig:scheme}
\end{figure}

% ===================================================================
% METHODS SECTION
% ===================================================================
\section{Methods}\label{sec:methods}
Our methodology infers CCC by learning a quantum-mechanical transformation that models how cellular states shift from a non-interacting to an interacting environment. The framework comprises three main stages: (1) pre-processing single-cell transcriptomic data to define baseline and target distributions; (2) specify a PQC to represent the state transformation; and (3) use a multi-stage hybrid optimization strategy to learn circuit parameters that best capture the communication dynamics.

\subsection{Data Processing and Quantum State Encoding}
\label{subsec:processing_encoding}
Our framework takes as input scRNA-seq data from two distinct cell types (e.g., CT1 and CT2) collected under, both non-interacting (e.g., mono-culture) and interacting (e.g., co-culture) conditions (Fig.~\ref{fig:scheme}). The data were pre-processed using Scanpy \cite{wolf2018scanpy}, including total-count normalization and logarithmic transformation, $X' = \texttt{log}(1-X)$. After pre-processing, we selected, for each cell type, a subset of genes/features most relevant to the biological context under study.

To map the continuous expression profile onto the discrete basis states of the quantum system, we binarized the expression of each selected gene. Each gene is considered ``active" (state 1) or ``inactive" (state 0) using a defined threshold; here, a gene was considered active if its log-normalized expression was greater than zero. This binarization was biologically principled since scRNA-seq data is inherently sparse, and zero observations often reflect genuinely low-expression states rather than purely technical dropout \cite{qiu2020embracing}. Binary representations of scRNA-seq data have been shown to faithfully capture cell-type-level biological variation \cite{bouland2021differential}, and the active/inactive threshold  typically mirrors the characteristic ON/OFF expression switching observed in regulatory genes at single-cell resolution \cite{korthauer2016statistical}. This procedure converts each cell's transcriptomic profile into a  bitstring, $s \in \{0, 1\}^{2d}$, where $d$ is the number of selected genes. From the binarized data, we subsequently computed empirical joint frequency counts, $C(s)$ for each unique cellular state $s$.

These frequency counts are then used to construct the two primary inputs for our quantum model: the initial quantum state and the classical target distributions.
\begin{enumerate}
    \item \textbf{Baseline State Amplitudes:} To prepare the initial state of the quantum circuit, counts from the non-interacting (mono-culture) cells, $C_{\text{Mo}}(s)$, were L2-normalized to define the state vector's amplitudes, $\alpha^{\text{Mo}}_s = \frac{C_{\text{Mo}}(s)}{\sum_{s' \in \{0,1\}^d} C_{\text{Mo}}(s')^2}$:
    \begin{equation}
        \alpha^{\text{Mo}}_s = \frac{C_{\text{Mo}}(s)}{\sqrt{\sum_{s' \in \{0,1\}^d} C_{\text{Mo}}(s')^2}}.
        \label{eq:amplitude_mo}
    \end{equation}
    These amplitudes define the individual \textbf{baseline state vectors}, $\ket{\psi^{\text{Co}}_{\text{CT1}}}$ and $\ket{\psi^{\text{Mo}}_{\text{CT2}}}$.

    \item \textbf{Target Probability Distributions:} To define the classical target for our cost function, the counts from the interacting (co-culture) cells, $C_{\text{Co}}(s)$, were first L2-normalized to produce a vector of target amplitudes, $\alpha^{\text{Co}}_s$. These amplitudes were then squared to yield the final target probability distributions, $Q_{\text{Co}}(s)$:
    \begin{equation}
        \alpha^{\text{Co}}_s = \frac{C_{\text{Co}}(s)}{\sqrt{\sum_{s'} C_{\text{Co}}(s')^2}} \quad \text{and} \quad Q_{\text{Co}}(s) = |\alpha^{\text{Co}}_s|^2.
        \label{eq:prob_co}
    \end{equation}
\end{enumerate}

\subsection{The Quantum Transformation Model}
\label{subsec:quantum_model}
Our model is a PQC \cite{benedetti2019parameterized} acting on a combined system of $N+M$ qubits, comprising an $N$-qubit logical register for CT1 and an $M$-qubit logical register for CT2. The circuit's evolution is described by the unitary transformation:
\begin{equation}
    \ket{\psi'} = U(\tau, \theta) \ket{\Psi_{\text{Mo}}}.
    \label{eq:unitary_evolution}
\end{equation}
Here, $\ket{\Psi_{\text{Mo}}}$ is the \textbf{global initial state}, representing the two cell types in isolation. It was constructed by taking the tensor product of the individual baseline state vectors (Eq.~\ref{eq:amplitude_mo}):
\begin{equation}
    \ket{\Psi_{\text{Mo}}} = \ket{\psi^{\text{Mo}}_{\text{CT1}}} \otimes \ket{\psi^{\text{Mo}}_{\text{CT2}}}.
    \label{eq:initial_state_global}
\end{equation}
The operator $U(\tau, \theta)$ models the intercellular communication and is composed of a sequence of entangling gates connecting the two logical registers. It is defined by its discrete \textbf{topology} $\tau$ and continuous \textbf{parameters} $\theta$.

\subsection{Hybrid Optimization Strategy}
\label{subsec:optimization}
The PQC was trained using a classical optimization loop \cite{cerezo2021variational} to find the optimal circuit parameters $(\tau_{\text{opt}}, \theta_{\text{opt}})$ that minimize a cost function based on the Kullback-Leibler (KL) divergence \cite{kullback1951information}.

\subsubsection{Objective Function}
The cost function, $\mathcal{L}(\tau, \theta)$, measures the dissimilarity between the marginal distributions of the circuit's output state, $\ket{\psi'}$, and the target marginal distributions from the interacting data (Eq.~\ref{eq:prob_co}):
\begin{equation}
    \mathcal{L}(\tau, \theta) = D_{\text{KL}}(P_{\psi'}(\text{CT1}) \parallel Q_{\text{Co}}(\text{CT1})) + D_{\text{KL}}(P_{\psi'}(\text{CT2}) \parallel Q_{\text{Co}}(\text{CT2})),
    \label{eq:kl_cost}
\end{equation}
where $P_{\psi'}(\text{CT}_k)$ is the marginal probability distribution for cell type $k$ obtained by simulating the PQC. Note that the cost was computed over marginal distributions independently for each cell type. Cross-cell-type correlations were not directly measured but are instead implicitly encoded by the entangling topology $\tau$, which must create the inter-register dependencies required to simultaneously satisfy both marginal constraints.

\subsubsection{Topology Search (\texorpdfstring{$\tau$}{tau})}
Finding the optimal entangling topology $\tau$ is an NP-hard optimal sequence search problem \cite{lucas2014ising}, as it required selecting both the best subset of gates and their optimal application order. Because exhaustive brute-force searches are intractable, we adopted a two-stage strategy: heuristic pruning of the search space, followed by the application of one of several search algorithms.

For the discrete topology search, we used controlled-RX (CRX) gates with a fixed angle of $\pi/2$ as the basic building blocks. This choice enabled the detection of weaker correlations via partial entanglement, as detailed in the circuit construction pipeline in Appendix~\ref{appendix:circuit_construction}.

\paragraph{Heuristic Pruning of Candidate Gates} To guide the search, we first identified a high-potential candidate set of entangling gates, $\mathcal{C}$, by analyzing the difference between the global density matrices of the non-interacting and interacting systems (see Appendix~\ref{appendix:pruning} for details). By applying a threshold to the elements of the difference matrix, $\Delta\rho$ (Eq.~\ref{eq:dens_diff_appendix}), we generated a reduced list of CNOT gates that were most likely to facilitate the required state transformation. This pruned set $\mathcal{C}$ was the input to all subsequent search algorithms.

\paragraph{Search Algorithms} 
We subsequently developed and compared three distinct strategies to search for the optimal topology within the pruned candidate set $\mathcal{C}$:
\begin{enumerate}
    \item \textbf{Algorithm 1: Iterative Local Search:} A classical greedy heuristic \cite{hoos2018stochastic} that simultaneously explored gate selection and ordering by testing addition, insertion, and deletion moves in each iteration (see Appendix~\ref{appendix:algo1} for full details).
    \item \textbf{Algorithm 2: Multi-Epoch Sequential Construction:} A faster, stochastic greedy search that used multiple random starting points to build candidate sequences, followed by a refinement pruning step applying an Occam's Razor parsimony criterion \cite{blumer1987occam} (see Appendix~\ref{appendix:algo2} for full details).
    \item \textbf{Algorithm 3: QUBO-based Variational Selection:} A quantum-native approach \cite{farhi2014quantum, peruzzo2014variational} that decoupled the problem into a gate selection stage, solved with VQE or QAOA, and a final classical permutation stage (see Appendix~\ref{appendix:algo3} for full details).
\end{enumerate}
Table~\ref{tab:algo_comparison} summarizes the strengths and weaknesses of each algorithm. Based on our empirical results, we selected Algorithm 2 for the primary analyses because it offers a strong balance between computational efficiency and solution quality. In practice, all three algorithms achieved similar levels of KL minimization. Algorithm 1 was the most stable but also the most computationally intensive. Algorithm 2 was faster and provides a reliable estimate of the achievable minimization, and Algorithm 3 was a forward-looking approach that used quantum-assisted gate selection to narrow down permutation candidates, with the potential to outperform Algorithm 1 given a sufficiently large initial candidate pool.

\begin{table}[h!]
\centering
\caption{Comparison of Topology Search Algorithms}
\label{tab:algo_comparison}
\renewcommand{\arraystretch}{1.3}
\begin{tabular}{|p{0.2\textwidth}|p{0.35\textwidth}|p{0.35\textwidth}|}
\hline
\textbf{Algorithm} & \textbf{Strengths} & \textbf{Weaknesses} \\ \hline \hline
\textbf{1. Iterative Local Search} &
\begin{itemize}
    \item Holistically explores the combined selection and permutation space.
    \item Effective at finding complex, order-dependent interactions.
    \item Flexible search through addition, insertion, and deletion moves.
\end{itemize} &
\begin{itemize}
    \item Computationally expensive, scales with sequence length.
    \item Greedy nature; not guaranteed to find the global optimum.
\end{itemize} \\ \hline
\textbf{2. Multi-Epoch Sequential Construction} &
\begin{itemize}
    \item Computationally faster than full local search.
    \item Stochastic starting points reduce risk of getting stuck in poor local minima.
    \item Good balance of exploration and speed.
\end{itemize} &
\begin{itemize}
    \item Forward construction is less thorough in exploring permutations.
    \item May miss solutions where a key gate must be placed early in the sequence.
\end{itemize} \\ \hline
\textbf{3. QUBO-based Variational Selection} &
\begin{itemize}
    \item Maps the hard gate-selection problem to a physical ground state problem (path to quantum advantage).
    \item Can efficiently search over a vast number of gate combinations.
    \item Can be combined with classical methods for a hybrid approach.
\end{itemize} &
\begin{itemize}
    \item Two-stage process; decouples selection from ordering.
    \item Classical permutation post-processing is intractable for large numbers of selected gates ($k > 8$--$10$).
    \item VQE/QAOA are heuristic and not guaranteed to find the true ground state.
\end{itemize} \\ \hline
\end{tabular}
\end{table}

\subsubsection{Parameter Optimization (\texorpdfstring{$\theta$}{theta})}
For finer-grained modeling, the fixed-angle CRX($\pi/2$) gates used in the discrete topology search are promoted to a continuous ansatz. This was achieved by replacing each fixed gate with a fully parameterized CRX($\theta_i$) gate, allowing the model to learn the precise interaction strength. The final optimization step solved for the optimal vector of continuous parameters:
\begin{equation}
    \theta_{\text{opt}} = \arg\min_{\theta} \mathcal{L}(\tau_{\text{opt}}, \theta),
\end{equation}
where $\theta$ is the angle set to be optimized and initialized to zero ($\theta_i=0$).
This continuous optimization problem was solved using a classical gradient-free algorithm \cite{powell1994direct}, specifically L-BFGS-B \cite{liu1989limited} or COBYLA \cite{powell1994direct}, applied to the fixed topology $\tau_{\text{opt}}$.

\subsection{Implementation Details}
All data processing and analyses were performed in Python. Single-cell data were handled using \texttt{scanpy} \cite{wolf2018scanpy}. The quantum circuits and simulations were implemented in IBM's Qiskit framework \cite{javadiabhari2024quantum, Qiskit}, using the \texttt{qiskit\_aer} simulator \cite{qiskit_aer}. Classical optimization used routines from \texttt{SciPy.optimize} \cite{virtanen2020scipy}. Code for our quantum generative framework is available at GitHub (\url{https://github.com/cailab-tamu/QuantumXCT}).



% ===================================================================
% RESULTS SECTION
% ==================================================================
\section{Results}\label{sec:results}
We evaluated the performance of QuantumXCT in two distinct stages. First, we used a controlled synthetic dataset as a proof-of-concept to show that the framework can learn predefined interaction dynamics and recover ground-truth rules (details in Appendix~\ref{appendix:spatial_sim_cells}). Second, we applied the model to real scRNA-seq datasets to assess its ability to identify novel CCC channels in complex biological environments.

\subsection{Benchmarking via Synthetic State-to-State Transformations}\label{subsec:sim_results}
To establish the utility of our hybrid quantum-classical approach, we first benchmarked its ability to learn a high-dimensional probability distribution transformation using simulated cellular data. This synthetic dataset (Appendix~\ref{appendix:spatial_sim_cells}) provided a ground-truth environment, in which gene-gene and cell-cell interactions were explicitly defined, enabling quantitative evaluation of the accuracy of our topology search algorithms.

\subsubsection{Data Encoding and Experimental Setup}
Following the methodology in Section~\ref{subsec:processing_encoding}, we binarized the transcriptomic counts of selected gene sets into ordered bit-strings, where each bit represents the activity of a gene. These bit-strings define unique cellular states, which were then encoded as the basis states of a quantum system. The normalized frequency of these states determined the amplitudes of a state vector, $\ket{\psi}$, representing the entire cellular population in a high-dimensional Hilbert space.

For this controlled benchmark, we defined cell type 1 (CT1) using a 2-gene feature set ($G_{\text{CT1}} = \{g_{50}, g_{90}\}$) and cell type 2 (CT2) using a 5-gene feature set ($G_{\text{CT2}} = \{g_{60}, g_{70}, g_{71}, g_{80}\}$). This configuration resulted in a 7-qubit system, where the first two qubits represent CT1 and the remaining five represent CT2.

As illustrated in Figure~\ref{fig:sim_comparison}, the joint histograms of non-interacting cells (``Initial States") were used to construct the initial state vector, $\ket{\Psi_0}$. The histograms from the interacting cells (``Final Target States") defined the target distributions for the KL divergence cost function. We deployed two of our primary classical search heuristics to find the optimal entangling topology: the N-Wise Search (Algorithm~\ref{alg:local_search}, with $n=2$) and the Multi-Epoch Search (Algorithm~\ref{alg:multi_epoch}). Both algorithms were used to discover the optimal unitary transformation, $U(\tau_{\text{opt}}, \theta_{\text{opt}})$, that evolves the initial state distribution to best match the target distribution, thereby learning the underlying communication rules from the data.

As illustrated in Figure~\ref{fig:sim_comparison}A, the joint histograms of non-interacting cells (``Initial States'') were used to construct the initial state vector, $\ket{\Psi_0}$, while the histograms from interacting cells (``Final Target States'') defined the target distributions for the KL divergence cost function. We deployed two of our primary classical search heuristics---the N-Wise Search (Algorithm~\ref{alg:local_search}, with $n=2$) and the Multi-Epoch Search (Algorithm~\ref{alg:multi_epoch})---to discover the optimal entangling topology. Both algorithms were used to identify the optimal unitary transformation, $U(\tau_{\text{opt}}, \theta_{\text{opt}})$, that evolves the initial state distribution to best match the target distribution, thereby learning the underlying communication rules from the data. Crucially, both heuristics successfully converged to high-fidelity solutions, despite discovering distinct circuit topologies (Fig.~\ref{fig:sim_comparison}B,~C).


\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{fig_2_QuantumXCT_pred_qsim_cells.pdf}
\caption{\textbf{Validation of QuantumXCT on synthetic single-cell data.} Our framework successfully learns the transformation from a non-interacting to an interacting cellular state using simulated data with ground-truth rules.
\textbf{(A) Optimization Workflow.} Input joint histograms of non-interacting cells define the \textbf{Initial States} ($\ket{\Psi_0}$), while interacting cell histograms define the \textbf{Final Target States} ($\ket{\Psi_f}$). The objective is to identify a unitary transformation, $U(\tau_{\text{opt}}, \theta_{\text{opt}})$, that evolves the initial distribution to best match the target.
\textbf{(B) N-Wise Search Performance.} Results for the Iterative Local Search (Algorithm 1, $n=2$). The panel shows the discovered quantum circuit topology, the KL divergence convergence during angle optimization, and the final state occupancy. The optimized QXCT distribution (light purple) shows high fidelity to the ``Interacting" ground-truth (dark purple).
\textbf{(C) Multi-Epoch Search Performance.} Corresponding results for the Multi-Epoch Search (Algorithm 2). Despite identifying a topologically distinct entangling circuit, the model achieves comparable convergence and occupancy matching. Both heuristics validate the framework's ability to learn the underlying dynamics and identify key regulatory nodes.}
\label{fig:sim_comparison}
\end{figure}



\subsubsection{Fidelity of Learned Distributions and Topological Interpretability}
The optimization results for the synthetic benchmark demonstrate that QuantumXCT successfully learned the underlying causal structure of the cellular system. As shown in Figure~\ref{fig:sim_comparison}, both the N-Wise and Multi-Epoch search heuristics converged to low KL divergence minima. While not a perfect replication, the output distributions of the optimized circuits (labeled ``QXCT") correctly modeled the key transformations from the non-interacting baseline. Both algorithms learned to suppress dominant non-interacting states while increasing the populations of interaction-induced states, demonstrating the model's ability to capture the directional shift in the high-dimensional probability landscape.

To validate the biological relevance of the discovered circuits, we mapped the entangling gates to the gene-qubit assignments: $\{q_0:g_{50}, q_1:g_{90}\}$ for CT1, and $\{q_2:g_{60}, q_3:g_{70}, q_4:g_{71}, q_5:g_{80}\}$ for CT2.

In the \textbf{N-Wise Search} (Fig.~\ref{fig:sim_comparison}B), the algorithm discovered a set of entanglements that represent a compressed, functionally equivalent model of the ground-truth pathways. It perfectly recovered the primary ligand-receptor interaction by entangling $q_0$ with $q_2$ ($g_{50} \to g_{60}$). Instead of learning the entire multi-step cascade literally, the algorithm utilized powerful ``functional shortcuts." For example, it directly entangled the initial driver $q_0$ ($g_{50}$) with the downstream gene $q_4$ ($g_{71}$), effectively summarizing the initial part of the CT2 GRN defined in Appendix~\ref{appendix:lr_grn_benchmark}. Similarly, it captured the full intercellular signaling arc by linking CT2's receptor $q_2$ ($g_{60}$) directly to CT1's final target $q_1$ ($g_{90}$). Most remarkably, the algorithm uncovered the complex feedback logic by entangling both the intercellular source $q_5$ ($g_{80}$) and the intracellular target $q_1$ ($g_{90}$) back to the initial driver $q_0$ ($g_{50}$). This demonstrates that the PQC learns the most efficient quantum operations that enforce the co-dependencies between key regulatory nodes ($g_{50}, g_{80}, g_{90}$), rather than simply recapitulating a biological wiring diagram.

The \textbf{Multi-Epoch Search} (Fig.~\ref{fig:sim_comparison}C) arrived at a topologically distinct solution that nonetheless achieved comparable fidelity and reinforced the same biological principles. This heuristic identified $g_{50}$ as a central ``hub" by entangling its corresponding qubit ($q_0$) with multiple downstream genes in the CT2 cascade ($q_2, q_4, q_5$). Crucially, despite the different topology, it converged on the same key functional relationships found by the N-Wise search, such as the direct influence of the CT2 cascade on CT1's target ($q_2 \to q_1$ and $q_2 \to q_0$). The emergence of these consistent entangling patterns across different search algorithms strongly suggests that our framework is robustly uncovering the dominant correlations dictated by the underlying GRN and CCC channels.



\subsection{Single-Cell Communication Inference using Ovarian Cancer Cell Lines}\label{subsec:scrna_seq_res}
To demonstrate utility in a real biological setting, we applied QuantumXCT to an ovarian cancer dataset in which cancer cells interact with fibroblasts, inducing their transition into cancer-associated fibroblasts (CAFs) \cite{mori2024targeting}. In this case study, the mono-cultured state represents cell lines grown separately, thus with no CCC, whereas co-culture represents the interacting state where CCC drives the CAF phenotype. We hypothesize our framework is well-suited to model the shifts between states by learning an optimal entangling topology ($U(\tau, \theta)$) that captures the joint effects of intracellular GRNs and intercellular ligand-receptor (LR) interactions.

For this purpose, we used a moderate density matrix cutoff ($\delta\rho>0.01$) to prune the initial search space, focusing the algorithms on the most significant potential interactions. We then applied two primary search heuristics to identify potential CCC interactions; the results are shown in Fig.~\ref{fig:ovarian_cancer}, with a detailed breakdown of gate contributions provided in Table~\ref{tab:kl_comp_analysis}.

The \textbf{N-Wise Search} (Fig.~\ref{fig:ovarian_cancer}A) converged on a highly parsimonious 3-gate topology that reduced the KL divergence from an initial 0.317 to an optimal 0.093. The resulting network correctly identified a core communication hub consisting of \texttt{PDGFB}, \texttt{PDGFRB}, and \texttt{STAT3}. The ablation analysis (Table~\ref{tab:kl_comp_analysis}) revealed that two interactions, \texttt{PDGFRB $\to$ PDGFB} and \texttt{STAT3 $\to$ PDGFRB}, were responsible for over 90\% of the total cost function reduction, highlighting them as the dominant regulatory axes in this model. The biologically constrained network plot visualizes this, showing the known intercellular \texttt{PDGFB-PDGFRB} link as the primary communication channel.

The \textbf{Multi-Epoch Search} (Fig.~\ref{fig:ovarian_cancer}B) discovered a larger, 5-gate topology, and reinforced the same core biological finding. This algorithm also identified the \texttt{PDGFB-PDGFRB-STAT3} hub as the essential component, with the same two interactions accounting for the vast majority of the KL reduction (from 0.326 to 0.079). Notably, this more exploratory search also proposed links such as \texttt{PDGFB $\to$ TGFBR2}.

A key insight comes from our two-stage optimization strategy. The initial topology search was performed with fixed CRX($\pi/2$) gates to efficiently find a promising interaction structure. The final ablation analysis (Table~\ref{tab:kl_comp_analysis}), however, was performed after a fine-tuning step where all gate angles were optimized together, starting from zero. This allowed us to dissect the true contribution of each interaction. The Multi-Epoch strategy revealed that while the \texttt{PDGFB $\to$ TGFBR2} link may have been beneficial during the initial search, its final optimized contribution was negligible and slightly increased the KL divergence (+0.014). This demonstrates the power of our framework to not only discover potential topologies but also to post-analytically distinguish core, important driver interactions from those that are redundant or non-essential in the final optimized model.

Ultimately, both the distinct algorithms converged on the same core biological insight: the cancer $\to$ CAF polarization was driven by a CCC feedback loop involving \texttt{PDGFB}, \texttt{PDGFRB}, and \texttt{STAT3}. This confirms the robustness of the QuantumXCT framework and its ability to distill complex quantum entanglements into interpretable biological networks.

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{Fig3_co_mo_ovarian.pdf}
\caption{\textbf{QuantumXCT discovers a core communication hub in an ovarian cancer dataset.} Our framework was applied to scRNA-seq data from cancer cells and fibroblasts to model their interaction.
\textbf{(A) N-Wise Algorithm Results.} The parsimonious 3-gate quantum circuit (left) discovered by the Iterative Local Search and the corresponding biologically constrained interaction network (right). The network plot visualizes the primary intercellular link (\texttt{PDGFB-PDGFRB}) and the intracellular GRN connections within the identified \texttt{\{PDGFB, PDGFRB, STAT3\}} hub.
\textbf{(B) Multi-Epoch Algorithm Results.} The larger 5-gate circuit is generated by the stochastic search heuristic. Although topologically different, the resulting network converges on the same core hub, highlighting the robustness of the framework. This solution proposes an additional link to \texttt{TGFBR2}, whose low impact is quantified by the contribution analysis in Table~\ref{tab:kl_comp_analysis}, demonstrating the method's ability to distinguish driver interactions from less significant ones.
}
\label{fig:ovarian_cancer}
\end{figure}

\begin{table}[h!]
\centering
\caption{Sequential Gate Contribution Analysis for Final Optimized Topologies. This ablation study reveals the true contribution of each interaction after fine-tuning, allowing for the identification of the most impactful gates based on their percent  contribution to the total KL reduction.}
\label{tab:kl_comp_analysis}
\renewcommand{\arraystretch}{1.2}
\small 
\begin{tabular}{l l l r r r r}
\toprule
\textbf{Algorithm} & \textbf{Source} & \textbf{Target} & \textbf{$\theta_i$ (rad)} & \textbf{KL Value} & \textbf{KL $\Delta$} & \textbf{\% Contrib.} \\ \midrule \hline
\multicolumn{7}{l}{\textit{\textbf{N-Wise Search}}} \\
& Baseline & --- & --- & 0.317 & 0.000 & 0.0\% \\
& STAT3 & PDGFRB & 1.345 & 0.255 & -0.062 & 19.4\% \\
& PDGFB & STAT3  & 0.971 & 0.241 & -0.015 & 4.6\% \\
& PDGFRB & PDGFB & 1.523 & 0.093 & -0.147 & 46.5\% \\ \midrule
\multicolumn{7}{l}{\textit{\textbf{Multi-Epoch Search}}} \\
& Baseline & --- & --- & 0.326 & 0.000 & 0.0\% \\
& STAT3 & PDGFRB & 1.416 & 0.255 & -0.071 & 21.8\% \\
& PDGFRB & PDGFB & 1.433 & 0.082 & -0.173 & 53.0\% \\
& PDGFB & PDGFRB & 2.260 & 0.086 & +0.004 & 1.2\% \\
& PDGFRB & STAT3 & 1.3e-07 & 0.079 & -0.007 & 2.0\% \\
& PDGFB & TGFBR2 & 1.8e-05 & 0.093 & +0.014 & 4.3\% \\ \bottomrule
\end{tabular}
\end{table}

% ===================================================================
% DISCUSSION
% ===================================================================
\section{Discussion}\label{sec:discussion}
The emergence of single-cell transcriptomics has necessitated a shift from descriptive biology toward predictive, dynamical modeling. However, the prevailing reliance on static LR databases inherently limits the discovery of \textit{de novo} or context-specific cellular communication channels \cite{armingol2024diversification, jin2021inference}. Here, we introduce \textbf{QuantumXCT}, a hybrid quantum-classical generative framework that reframes CCC not as a search for interacting pairs, but as a learning unitary transformation between cellular probability distributions.

\subsection{Interpretability of Quantum-to-Biological Transcription}\label{subsec:disc_interpretability}
A recurring critique of QML is the ``black-box'' nature of parameterized circuits \cite{benedetti2019parameterized, cerezo2021variational}. We address this directly by demonstrating that the optimized entangling topology ($\tau_{\text{opt}}$) is not merely a computational artifact, but a structured representation of biological logic. By mapping the discovered gates back onto a biologically constrained interaction network (Fig.~\ref{fig:ovarian_cancer}), we obtain a human-interpretable ``relay map'' of intercellular interaction.

Importantly, our sequential gate contribution analysis (Table~\ref{tab:kl_comp_analysis}) allows us to ``ablate'' the model post-optimization. In the ovarian cancer model, the vast majority of the KL divergence reduction, nearly 90\%, was driven by the specific \texttt{PDGFB-PDGFRB-STAT3} hub \cite{mori2024targeting}. This indicates that our quantitative ranking separate high-impact ``driver'' interactions from secondary ``passenger'' correlations that can confound classical co-expression benchmarks \cite{armingol2024diversification, dimitrov2022comparison}. Whereas classical methods such as CellChat \cite{jin2021inference, jin2025cellchat} report a communication probability based on the co-expression of known LR pairs, QuantumXCT quantifies the \textit{functional contribution} of each interaction to the global transcriptomic state change, as evidenced by the sequential ablation results in Table~\ref{tab:kl_comp_analysis}. This shift from co-expression to functional impact constitutes the central methodological advance of the framework. Note that, in this work, ``impact" refers to changes in cellular state distributions rather than experimentally validated functional or phenotypic effects.

\subsection{Algorithmic Robustness and Convergence} \label{subsec:disc_robustness}
The stability of QuantumXCT is reflected in the convergence of disparate search heuristics on the same biological ground truth \cite{hoos2004stochastic}. Although the N-Wise (Algorithm~\ref{alg:local_search}) and Multi-Epoch (Algorithm~\ref{alg:multi_epoch}) searches produced topologically distinct circuits, both yield functionally equivalent models of the \texttt{PDGFB} signaling axis. This suggests that the quantum state space is naturally conducive to representing the underlying network connectivity, such that multiple entangling paths can successfully encode the same high-dimensional distributional shift \cite{benedetti2019parameterized}.

\subsection{Binarization as a Biologically Motivated Encoding}
\label{subsec:disc_binarization}
A natural question concerns whether the binarization step---converting log-normalized expression values to an active/inactive binary state---discards biologically meaningful gradients of expression. We argue that for the specific purpose of quantum state encoding this compression is not only tractable but biologically principled. Single-cell transcriptomic data are inherently sparse, and zero observations following log1p-normalization reflect genuine low-expression states rather than purely technical dropout \cite{qiu2020embracing}. Binary representations of scRNA-seq data faithfully capture cell-type-level biological variation \cite{bouland2021differential}, and as scRNA-seq datasets grow larger and sparser the downstream conclusions drawn from binarized representations remain consistent with count-based analyses \cite{vandenBerge2023consequences}. The active/inactive threshold moreover mirrors the characteristic ON/OFF expression switching observed in regulatory genes at single-cell resolution \cite{korthauer2016statistical}. Importantly, the QuantumXCT framework does not require binarization to recover quantitative gradients of interaction strength. This is instead captured through the continuous optimization of gate angles $\theta$ in Section~\ref{subsec:optimization}. The binarization step defines the \textit{topology} of the probability landscape, e.g., which cellular states are accessible and with what frequency, while the continuous parameters learn the \textit{strength} of the transitions between those states. Future extensions could explore multi-level quantization of expression (e.g., low/medium/high) at the cost of exponentially larger qubit registers, requiring advances in quantum hardware beyond the current NISQ era
\cite{preskill2018quantum}.

\subsection{Marginal Approximation, Scalability, and the Path to Full Joint
Inference}
\label{subsec:disc_marginal}
The cost function in Eq.~\ref{eq:kl_cost} minimizes the sum of KL divergences \cite{kullback1951information} between the \textit{marginal} output distributions of the PQC and the empirical target, evaluated independently for each cell type. This design is not merely a computational convenience but a biological necessity: the two cell populations are experimentally distinct, each with their own gene selection, cell count, and expression landscape. The transcriptomic state of CT1 is encoded in a matrix of dimensions $n_{\text{cells}}^{\text{CT1}} \times g_{\text{CT1}}$, and that of CT2 in a matrix of dimensions $n_{\text{cells}}^{\text{CT2}} \times
g_{\text{CT2}}$, where the gene sets and cell counts need not be equal. Because each cell type probability distribution is defined locally---over the activity states of its own gene set and measured only from its own cells---the two marginal distributions are naturally isolated, and each KL
divergence term measures a well-defined, self-contained discrepancy. The joint quantum state $\ket{\Psi_{\text{Mo}}} = \ket{\psi^{\text{Mo}}_{\text{CT1}}}
\otimes \ket{\psi^{\text{Mo}}_{\text{CT2}}}$ is then constructed via the tensor (Kronecker) product of these two independently defined state vectors (Eq.~\ref{eq:initial_state_global}), encoding their non-interacting baseline as a separable state. The unitary $U(\tau, \theta)$ is then responsible for introducing the entanglement that models cross-cell-type communication, and the optimizer minimizes both marginal KL terms simultaneously, forcing the circuit to learn inter-register dependencies without ever requiring a joint measurement. This architecture is therefore not an approximation of a joint objective but the correct formulation for the biological problem: the distributions are genuinely local to their respective cell types, and the entangling topology $\tau$ \textit{is} the learned model of the communication between them. The convergence of independently run algorithms to the same \texttt{PDGFB-PDGFRB-STAT3} hub \cite{mori2024targeting} confirms that simultaneously minimizing both marginal terms is sufficient to identify the dominant functional axes of intercellular signaling. Nonetheless, future work with fault-tolerant quantum hardware could explore joint tomographic approaches to verify higher-order multi-gene dependencies that marginal objectives encode only implicitly \cite{preskill2018quantum, cerezo2021variational}.

A related scalability boundary was observed in our evaluation of Algorithm~3 (Appendix~\ref{appendix:algo3}). When the initial candidate set from the $\Delta\rho$ pruning step exceeds approximately 30 gates, the corresponding QUBO matrix \cite{lucas2014ising} becomes intractable for classical post-processing: the number of possible orderings of the selected gates grows factorially with $k$, and gate sets of $k > 8$--$10$ are not reliably handled by the permutation stage \cite{farhi2014quantum, peruzzo2014variational}. In practice on the ovarian cancer dataset, Algorithm~3 reduced a candidate pool to 6 gates, from which the quantum solver returned a 5-gate solution---yielding no meaningful parsimony gain over Algorithm~2 \cite{blumer1987occam}, which found a comparable topology without the VQE/QAOA overhead. In the current NISQ era \cite{preskill2018quantum}, this tradeoff is unfavorable for small gene sets. The QUBO formulation becomes genuinely advantageous, however, when the pre-selection step can provide thousands of candidate interactions---a scenario that becomes realistic on fault-tolerant devices capable of screening large interaction spaces in superposition. We therefore regard Algorithm~3 as a forward-looking component: not yet competitive at current hardware scales, but a natural target for quantum advantage as devices mature beyond the NISQ era \cite{cerezo2021variational}.

\subsection{Limitations and the ``Qubit Bottleneck''}
\label{subsec:disc_nisq}
Despite its predictive power, QuantumXCT is currently bounded by the ``qubit bottleneck'' inherent in the NISQ era \cite{preskill2018quantum}. The exponential scaling of the Hilbert space restricts our current implementation to targeted gene sets---typically $N+M \leq 10$ qubits, balanced across the two cell types. While this requires a focused pre-selection of genes, it also serves as a form of biological feature compression: operating in a low-qubit, high-information regime forces the model to identify the most parsimonious regulatory bottlenecks and helps mitigate the over-parameterization common in classical deep learning models \cite{cerezo2021variational}.

Exploratory analyses applying CellChat \cite{jin2021inference, jin2025cellchat} and scTenifoldXct \cite{yang2023sctenifoldxct} to the same ovarian cancer dataset are provided in the accompanying GitHub repository. Both methods recover the PDGFB--PDGFRB interaction, but they do so by testing co-expression of known pairs rather than learning the distributional shift between cellular states. CellChat assigns this interaction a low communication probability, consistent with its mass-action co-expression scoring \cite{jin2021inference}, whereas scTenifoldXct detects it through manifold alignment of GRNs \cite{yang2023sctenifoldxct}. QuantumXCT addresses a categorically different question: not \textit{which pairs are co-expressed}, but \textit{how much each interaction contributes to the global transformation of the transcriptomic state}. The sequential gate ablation (Table~\ref{tab:kl_comp_analysis}) demonstrates that the PDGFB--PDGFRB--STAT3 axis accounts for nearly 90\% of the KL divergence reduction---a functional quantification that is structurally inaccessible to co-expression frameworks regardless of their parameterization \cite{armingol2024diversification}.

% ===================================================================
% CONCLUSION
% ===================================================================
\section{Conclusion}\label{sec:conclusion}
QuantumXCT represents a tectonic shift in how cellular behavior is inferred from transcriptomics. Unlike traditional approaches that merely ``find'' interactions by matching ligands and receptors in curated databases \cite{armingol2024diversification, jin2021inference}, our framework models how cellular state distributions change between non-interacting and interacting conditions, and \textit{learns} the system-level impact of an interaction on the cell's full high-dimensional state. By treating CCC as a generative, probabilistic transformation, we move beyond static database matching toward a truly data-driven discovery platform. Our results on both synthetic and real datasets demonstrate that quantum circuits can capture the directional causality of signaling feedback loops, consistent with results from our companion quantum generative simulation study \cite{romero2025qsimcells}. As quantum hardware continues to scale beyond the NISQ era \cite{preskill2018quantum}, we anticipate that this framework will become a cornerstone for uncovering the latent ``rules'' governing complex cellular systems in oncology, immunology, and regenerative medicine.

\backmatter

\section*{Acknowledgments}

\section*{Declarations}
\begin{itemize}
\item\textbf{Funding}: This study was funded by the U.S. Department of Defense (DoD, GW200026) and the National Institute for Environmental Health Sciences (NIEHS, P30 ES029067) for J.J.C, Allen Endowed Chair in Nutrition \& Chronic Disease Prevention for R.S.C., and the Cancer Prevention \& Research Institute of Texas (CPRIT, RP230204) and Texas A\&M University 2026 Targeted Proposal Teams (TPT) funding program for J.J.C and R.S.C.\\
\item\textbf{Conflict of interest}: The authors have no conflict of interest.\\
\item\textbf{Data availability}: Our algorithm is publicly available on GitHub \url{https://github.com/cailab-tamu/QuantumXCT} along with the simulated data used in the study. The ovarian cancer scRNA-seq dataset used in this study is available at GSE224333.\\
\item\textbf{Author contribution}: S.R.: Conceptualization, Methodology, Formal analysis, Software, Writing - Original Draft. S.G: Investigation, Validation, Writing- Review \& Editing. R.S.C: Supervision, Resources. J.J.C: Conceptualization, Resources, Software, Supervision, Validation, Writing - Review \& Editing.
\end{itemize}


% ===================================================================
% APPENDICES
% ===================================================================
\begin{appendices}

\section{Common Algorithmic Components}
\label{appendix:common_components}
All algorithms developed for discovering the optimal entangling topology, $\tau$, share foundational components for circuit construction and evaluation. This section details these shared modules.

\subsection{Quantum Circuit Construction and Evaluation}
The evaluation of any candidate topology, $\tau$, involves constructing the corresponding quantum circuit, simulating it, and calculating a cost.

\subsubsection{Circuit Construction}\label{appendix:circuit_construction} 
A trial quantum circuit, $U(\tau)$, is assembled for a given sequence of entangling gates, $\tau = (G_k, \dots, G_1)$. The unitary operator is constructed as $U(\tau) = U_{G_k} \circ \dots \circ U_{G_1}$. During the discrete topology search phase, each gate $G_i$ in the sequence is implemented as a Controlled-RX gate with a fixed angle, CRX($\pi/2$). This strategic choice was made because a standard CNOT gate (equivalent to CRX($\pi$)) creates maximal entanglement, which might be too ``coarse" a tool for this problem. We reasoned that a discrete search using CNOTs might overlook weaker, yet biologically significant, correlations. By using CRX($\pi/2$), we allow the topology search to identify potential interactions based on their ability to create partial or ``mixed" entanglement, thereby capturing a wider range of potential inter- and intra-state interactions that minimize the cost function.

The final state of the system before measurement is $\ket{\psi'} = U(\tau)\ket{\Psi_{\text{Mo}}}$. Measurement operations are appended to each logical register (CT1 and CT2).


\subsubsection{Cost Function Evaluation}
The fitness of a circuit is quantified by its cost, $\mathcal{L}(\tau)$.
\begin{enumerate}
    \item \textbf{Quantum Simulation:} The circuit $U(\tau)$ is executed for \texttt{nshots}, yielding measurement counts $C_{\text{sim}}^{\text{CT}_k}(s)$ for each state $s$ in each logical register $k$.
    \item \textbf{Quantum Inferred Distribution Sampling:} The counts are normalized to produce marginal probability distributions from quantum sampled histograms (related to the amplitudes Eqs.~\ref{eq:amplitude_mo} and ~\ref{eq:prob_co}): $P_{\psi'}^{\text{CT}_k}(s) = C_{\text{sim}}^{\text{CT}_k}(s) / \texttt{nshots}$.
    \item \textbf{KL Divergence Calculation:} The total cost is the sum of KL divergences between the simulated and target distributions (from Eq.~\ref{eq:kl_cost}):
    \begin{equation}
        D_{\text{KL}}(P_{\psi'}^{\text{CT}_k} \parallel Q_{\text{Co}}^{\text{CT}_k}) = \sum_{s} P_{\psi'}^{\text{CT}_k}(s) \log \left( \frac{P_{\psi'}^{\text{CT}_k}(s)}{Q_{\text{Co}}^{\text{CT}_k}(s)} \right)
    \end{equation}
\end{enumerate}



\section{Heuristic Pruning of the Gate Search Space}
\label{appendix:pruning}

All topology search algorithms described in this work operate not on the complete set of all possible entangling gates, but on a reduced, high-potential candidate set, $\mathcal{C}$. This initial pruning step is critical for making the subsequent combinatorial and permutational searches tractable.

We guide the search by analyzing the difference between the global density matrices of the non-interacting and interacting systems. First, we define the global state vectors for the mono-culture (initial) and co-culture (target) systems as the tensor products of their respective individual state vectors, which are derived from the experimental data as described in the main text (Eqs.~\ref{eq:amplitude_mo} and \ref{eq:prob_co}):
\begin{align}
    \ket{\Psi_{\text{Mo}}} &= \ket{\psi^{\text{Mo}}_{\text{CT1}}} \otimes \ket{\psi^{\text{Mo}}_{\text{CT2}}} \\
    \ket{\Psi_{\text{Co}}} &= \ket{\psi^{\text{Co}}_{\text{CT1}}} \otimes \ket{\psi^{\text{Co}}_{\text{CT2}}}
\end{align}
The corresponding density matrices are then defined by the outer product, $\rho = \ket{\Psi}\bra{\Psi}$. We compute the difference between the target and initial density matrices:
\begin{equation}\label{eq:dens_diff_appendix}
    \Delta\rho = \rho_{\text{Co}} - \rho_{\text{Mo}}
\end{equation}
The matrix $\Delta\rho$ highlights the specific state-to-state transitions (i.e., the off-diagonal elements) and changes in state populations (i.e., the diagonal elements) required to evolve the system from the non-interacting to the interacting state. By applying a threshold to the elements of $\Delta\rho$, we identify the most significant state-to-state transitions. From this, we generate a reduced candidate set, $\mathcal{C}$, where each element is a (control, target) qubit pair that specifies a potential CRX($\pi/2$) gate. These pairs are selected because they are the most likely to facilitate the identified transitions. This pruned set $\mathcal{C}$ serves as the direct input for all subsequent topology search algorithms.

% ========================================================
%Algo 1
% ========================================================
\section{Algorithm 1: Iterative Local Search}
\label{appendix:algo1}

This appendix provides a detailed description of the \textit{Iterative Local Search} algorithm, a classical heuristic for topology discovery. The algorithm begins with the pruned candidate set $\mathcal{C}$ (Appendix~\ref{appendix:pruning}) and uses the evaluation pipeline from Appendix~\ref{appendix:common_components}. It directly addresses the combined gate selection and ordering problem by iteratively and sequentially applying three types of moves—insertion, addition, and deletion—to refine a sequence of entangling gates.

\subsection{Algorithmic Workflow: Sequential Local Search}
The algorithm operates within a main iterative loop that continues as long as any move within an iteration successfully improves the cost function. Unlike a standard local search that evaluates all neighbors before making a move, this algorithm executes three distinct phases in a fixed sequence within each iteration, immediately updating the working solution if a phase is successful. This aggressive, sequential approach is designed to rapidly descend the cost landscape, as outlined in Algorithm~\ref{alg:local_search}.

\begin{algorithm}[h!]
\caption{Iterative Local Search for Topology Discovery}
\label{alg:local_search}
\begin{algorithmic}[1]
\Statex \textbf{Input:} Candidate gate set $\mathcal{C}$, Target distributions $Q_{\text{Co}}$, Permutation length $n_{\text{choose}}$, Significance threshold \texttt{kl\_tol}.
\Statex \textbf{Output:} Optimal sequence $\tau_{\text{best}}$, Final cost $L_{\text{best}}$.
\State \textbf{Initialize:} $\tau_{\text{best}} \gets \emptyset$, $L_{\text{best}} \gets \mathcal{L}(\emptyset)$, \texttt{improvement\_made} $\gets \text{True}$.
\While{\texttt{improvement\_found}}
    \State \texttt{improvement\_made} $\gets \text{False}$
    
    \State \Comment{\textit{Phase 1: Single Gate Insertion}}
    \State $(\tau_{\text{cand}}, L_{\text{cand}}) \gets \text{FindBestSingleInsertion}(\tau_{\text{best}}, \mathcal{C}, \texttt{kl\_tol})$
    \If{$L_{\text{cand}} < (L_{\text{best}} - \texttt{kl\_tol})$}
        \State $\tau_{\text{best}} \gets \tau_{\text{cand}}$, $L_{\text{best}} \gets L_{\text{cand}}$, \texttt{improvement\_made} $\gets \text{True}$
    \EndIf
    
    \State \Comment{\textit{Phase 2: N-wise Permutation Addition (on updated sequence)}}
    \State $(\tau_{\text{cand}}, L_{\text{cand}}) \gets \text{FindBestPermutationAddition}(\tau_{\text{best}}, \mathcal{C}, n_{\text{choose}}, \texttt{kl\_tol})$
    \If{$L_{\text{cand}} < (L_{\text{best}} - \texttt{kl\_tol})$}
        \State $\tau_{\text{best}} \gets \tau_{\text{cand}}$, $L_{\text{best}} \gets L_{\text{cand}}$, \texttt{improvement\_made} $\gets \text{True}$
    \EndIf

    \State \Comment{\textit{Phase 3: Single Gate Deletion (on updated sequence)}}
    \State $(\tau_{\text{cand}}, L_{\text{cand}}) \gets \text{FindBestSingleDeletion}(\tau_{\text{best}})$
    \If{$L_{\text{cand}} < (L_{\text{best}} - \epsilon_{\text{prune}})$} \Comment{$\epsilon_{\text{prune}}$ is a small positive constant}
        \State $\tau_{\text{best}} \gets \tau_{\text{cand}}$, $L_{\text{best}} \gets L_{\text{cand}}$, \texttt{improvement\_made} $\gets \text{True}$
    \EndIf
\EndWhile

\State \textbf{Return} $\tau_{\text{best}}, L_{\text{best}}$
\end{algorithmic}
\end{algorithm}

\subsection{Phase Descriptions}
Each phase of the iteration attempts to find the best possible move of a specific type and accepts it based on a defined criterion.

\subsubsection{Phase 1: Single Gate Insertion}
This move probes the importance of gate ordering by finding the best single gate to insert and its optimal position within the current sequence, $\tau_{\text{current}}$. The search for the optimal gate-index pair $(G^*, i^*)$ is defined as:
\begin{equation}
    (G^*, i^*) = \arg\min_{G \in \mathcal{C} \setminus \tau_{\text{current}}, \, i \in [0, |\tau_{\text{current}}|]} \mathcal{L}(\text{Insert}(G, \tau_{\text{current}}, i))
\end{equation}
The resulting sequence $\tau_{\text{insert}} = \text{Insert}(G^*, \tau_{\text{current}}, i^*)$ is immediately adopted if it provides a cost reduction greater than the significance threshold, i.e., if $\mathcal{L}(\tau_{\text{insert}}) < (\mathcal{L}(\tau_{\text{current}}) - \texttt{kl\_tol})$.

\subsubsection{Phase 2: N-wise Permutation Addition}
Operating on the potentially updated sequence from the previous phase, this move considers adding a short, ordered sequence of new gates. The length of this sequence, $n$, is a user-definable parameter (\texttt{n\_choose}). This phase searches over all permutations $p$ of length $n$ drawn from the remaining candidate gates $\mathcal{C}_{\text{rem}} = \mathcal{C} \setminus \tau_{\text{current}}$. The best permutation $p^*$ to append is found by solving:
\begin{equation}
    p^* = \arg\min_{p \in \mathcal{P}_n(\mathcal{C}_{\text{rem}})} \mathcal{L}(\tau_{\text{current}} \oplus p)
\end{equation}
where $\oplus$ denotes sequence concatenation. The resulting sequence $\tau_{\text{add}} = \tau_{\text{current}} \oplus p^*$ is immediately adopted if it meets the significance threshold.

This move explicitly tests for synergistic effects between small, ordered groups of new gates. While the algorithm supports any integer $n$, the computational cost of this phase scales factorially with $n$ and polynomially with the size of $\mathcal{C}_{\text{rem}}$. Therefore, for practical applications, small values of $n$ are necessary. In this work, we set $n=2$, focusing the search on pairwise interactions, which we found provides a good balance between uncovering synergistic effects and maintaining computational tractability.


\subsubsection{Phase 3: Single Gate Deletion}
Finally, this move provides a crucial pruning mechanism to correct for earlier greedy steps. It finds the optimal index $i^*$ of a gate to remove from the current sequence by finding the move that yields the absolute lowest cost:
\begin{equation}
    i^* = \arg\max_{i \in [0, |\tau_{\text{current}}|-1]} \mathcal{L}(\text{Delete}(\tau_{\text{current}}, i))
\end{equation}
The resulting sequence, $\tau_{\text{del}} = \text{Delete}(\tau_{\text{current}}, i^*)$, is adopted if its cost is lower than the current cost by more than a small, fixed margin ($\mathcal{L}(\tau_{\text{del}}) < \mathcal{L}(\tau_{\text{current}}) - \epsilon_{\text{prune}}$). This less strict criterion allows the algorithm to remove redundant gates to favor parsimony, even for marginal cost improvements.





\section{Algorithm 2:  Multi-Epoch Sequential Construction}
\label{appendix:algo2}

This appendix provides a detailed description of the \textit{Multi-Epoch Sequential Construction} algorithm. This heuristic is designed as a faster, stochastic alternative to the exhaustive local search, aiming to balance a broad exploration of the solution space with a final selection principle that favors model parsimony. The algorithm begins with the pruned candidate set $\mathcal{C}$ (Appendix~\ref{appendix:pruning}) and utilizes the evaluation pipeline from Appendix~\ref{appendix:common_components}.

\subsection{Algorithmic Workflow}
The algorithm is composed of three interconnected phases. First, it explores the solution space via multiple \textbf{Forward Greedy Construction} epochs; an epoch only proceeds if the initial random gate improves upon the baseline. Second, an \textbf{Immediate Backward Greedy Refinement} is triggered \textit{if} a forward search yields a new best-so-far solution; this phase removes irrelevant gates to ensure each addition in the sequence is strictly necessary. Finally, after all epochs are complete, a global selection phase based on Occam's Razor determines the final result. The process is outlined in Algorithm~\ref{alg:multi_epoch}.



\begin{algorithm}[h!]
\caption{Multi-Epoch Construction with Path Refinement and Occam's Razor}
\label{alg:multi_epoch}
\begin{algorithmic}[1]
\Statex \textbf{Input:} Candidate gate set $\mathcal{C}$, Target distributions $Q$, Epochs $N_{\text{epochs}}$, Threshold $\epsilon$ (\texttt{kl\_tol}).
\Statex \textbf{Output:} Optimal gate sequence $\tau^*$, Final cost $L^*$.
\State \textbf{Initialize:} $\tau_{\text{best}} \gets \emptyset$, $L_{\text{best}} \gets \mathcal{L}(\emptyset)$, $\mathcal{H}_{\text{eval}} \gets \{(L_{\text{best}}, \emptyset)\}$, $L_{\emptyset} \gets L_{\text{best}}$.
\State $\mathcal{C}_{\text{shuffled}} \gets \text{Shuffle}(\mathcal{C})$

\State \Comment{\textit{Phase 1: Multi-Epoch Exploration \& Refinement}}
\For{epoch from $1$ to $\min(N_{\text{epochs}}, |\mathcal{C}|)$}
    \State $G_{\text{start}} \gets \mathcal{C}_{\text{shuffled}}[\text{epoch}]$
    \State $L_{\text{start}} \gets \mathcal{L}((G_{\text{start}}))$
    
    \If{$L_{\text{start}} < L_{\emptyset}$} \Comment{Proceed only if $G_{\text{start}}$ improves on baseline}
        \State \Comment{Step 1.1: Greedy Forward Construction}
        \State $(\mathcal{H}_{\text{path}}, \tau_{\text{path}}, L_{\text{path}}) \gets \text{GreedyForward}((G_{\text{start}}), \mathcal{C})$
        \State $\mathcal{H}_{\text{eval}} \gets \mathcal{H}_{\text{eval}} \cup \mathcal{H}_{\text{path}}$
        
        \If{$L_{\text{path}} < L_{\text{best}}$} \Comment{New global champion found on this path}
            \State $L_{\text{best}} \gets L_{\text{path}}, \tau_{\text{best}} \gets \tau_{\text{path}}$
            
            \State \Comment{Step 1.2: Immediate Greedy Removal (Refinement)}
            \State $(\mathcal{H}_{\text{rem}}, \tau_{\text{rem}}, L_{\text{rem}}) \gets \text{GreedyRemoval}(\tau_{\text{best}}, L_{\text{best}}, \epsilon)$
            \State $\mathcal{H}_{\text{eval}} \gets \mathcal{H}_{\text{eval}} \cup \mathcal{H}_{\text{rem}}$
            
            \If{$L_{\text{rem}} < L_{\text{best}}$}
                \State $L_{\text{best}} \gets L_{\text{rem}}, \tau_{\text{best}} \gets \tau_{\text{rem}}$
            \EndIf
        \EndIf
    \EndIf
\EndFor

\State \Comment{\textit{Phase 2: Global Selection via Occam's Razor}}
\State Sort $\mathcal{H}_{\text{eval}}$ by sequence length $|\tau|$ in ascending order.
\State $(\tau^*, L^*) \gets \text{First element of sorted } \mathcal{H}_{\text{eval}}$
\For{each $(L_i, \tau_i) \in \text{sorted } \mathcal{H}_{\text{eval}}$}
    \If{$L_i < (L^* - \epsilon)$} \Comment{Accept longer sequence only if gain $> \epsilon$}
        \State $\tau^* \gets \tau_i, L^* \gets L_i$
    \EndIf
\EndFor

\State \textbf{Return:} $\tau^*, L^*$
\end{algorithmic}
\end{algorithm}


\subsection{Phase Descriptions}

\subsubsection{Phase 1: Multi-Epoch Forward Construction and Refinement}
This phase explores distinct regions of the solution space by initiating multiple independent, stochastic greedy searches. For each epoch, a candidate gate $G_{start}$ is selected from the shuffled set $\mathcal{C}_{shuffled}$. To maintain computational efficiency, a full forward greedy search is only initiated if this initial single-gate sequence improves upon the baseline empty circuit: 
\begin{equation}
\mathcal{L}((G_{start})) < \mathcal{L}(\emptyset)
\end{equation}



\begin{itemize}
    \item \textbf{Forward Greedy Construction:} If the starting gate is promising, the algorithm performs an iterative constructive search. At each step $k$, it identifies the optimal gate to append from the candidate set:
    \begin{equation}
    G^*_{k+1} = \arg\min_{G \in \mathcal{C} \setminus \tau_k} \mathcal{L}(\tau_k \oplus G)
    \end{equation}
    The new sequence $\tau_{k+1} = \tau_k \oplus G^*_{k+1}$ is accepted if $\mathcal{L}(\tau_{k+1}) < \mathcal{L}(\tau_k)$. This process continues until no single gate addition can improve the cost or the maximum depth is reached. The entire history of evaluated sequences is recorded in $\mathcal{H}_{eval}$.

    \item \textbf{Immediate Backward Refinement:} If the forward search yields a sequence $\tau_{path}$ that is a new global champion ($\mathcal{L}(\tau_{path}) < L_{best}$), a refinement step is triggered to prune redundant gates. Starting with $\tau_0 = \tau_{path}$, the algorithm evaluates the removal of every gate in the current sequence to identify the position $i^*$ that yields the minimum cost:
    \begin{equation}
    i^* = \arg\min_{i \in [0, |\tau_k|-1]} \mathcal{L}(\text{Delete}(\tau_k, i))
    \end{equation}
    The pruned sequence $\tau_{k+1} = \text{Delete}(\tau_k, i^*)$ is accepted if and only if $\mathcal{L}(\tau_{k+1}) < \mathcal{L}(\tau_k) - \delta$, where $\delta = 0.3 \cdot \epsilon$ represents a significance margin. This greedy positional removal continues iteratively until no single gate deletion satisfies the improvement criterion or the minimum depth is reached. This refinement phase ensures that any redundant gates introduced during the constructive phase are eliminated.
\end{itemize}

\subsubsection{Phase 2: Final Selection (Occam's Razor)}
To select the final topology $\tau^*$, the algorithm applies a model parsimony principle. The complete history of all unique sequences $\mathcal{H}_{eval}$ evaluated during all forward and backward phases is collected and sorted by sequence length $|\tau|$ in ascending order. 

The algorithm iterates through this sorted list, starting with the simplest model (the empty circuit). A more complex (longer) sequence $\tau_i$ is only accepted as the new best solution if its cost provides an improvement greater than the significance threshold $\epsilon$ (\texttt{kl\_tol}):
\begin{equation}
\mathcal{L}(\tau_i) < \mathcal{L}(\tau^*) + \epsilon
\end{equation}
This ensures that the final selected topology $\tau^*$ is the most parsimonious model that achieves a significant reduction in cost, effectively preventing over-parameterization and ensuring model robustness.




\section{Algorithm 3: QUBO-based Variational Selection}
\label{appendix:algo3}
This appendix details our quantum-native approach, which begins with the pruned candidate set $\mathcal{C}$ (Appendix~\ref{appendix:pruning}). This strategy reframes the gate selection problem as a Quadratic Unconstrained Binary Optimization (QUBO) problem, decoupling it into a quantum-assisted gate selection and a final classical ordering stage.



\subsection{Stage 1: KL-QUBO Formulation for Gate Selection}
The goal of this stage is to map the circuit optimization problem onto a QUBO framework. We define a binary vector $\mathbf{x} \in \{0, 1\}^N$, where $x_i = 1$ if the candidate CNOT gate $G_i \in \mathcal{C}$ is included in the circuit for a qubit pair, and $x_i = 0$ otherwise. The objective is to minimize the energy function:
\begin{equation}
    E(\mathbf{x}) = \sum_{i=1}^N Q_{ii} x_i + \sum_{i < j} Q_{ij} x_i x_j
\end{equation}

The construction of the QUBO matrix $Q$ proceeds in two steps:

\subsubsection{KL Divergence Matrix Construction}
We pre-compute a KL divergence matrix $M_{KL} \in \mathbb{R}^{N \times N}$ by evaluating the cost of single gates and gate pairs against the target distributions. Let $\mathcal{L}(\tau)$ denote the summed KL divergence of a circuit containing the sequence of gates $\tau$. The elements of $M_{KL}$ are defined as:
\begin{equation}
    (M_{KL})_{ij} = 
    \begin{cases} 
      \mathcal{L}(G_i) & \text{if } i = j \\
      \mathcal{L}(G_i, G_j) & \text{if } i \neq j
    \end{cases}
\end{equation}
where $L_{\emptyset} = \mathcal{L}(\emptyset)$ represents the baseline KL divergence of the circuit with no additional CNOT gates.

\subsubsection{QUBO Matrix Derivation}
The matrix $M_{KL}$ is transformed into the QUBO matrix $Q$ by isolating the individual and synergistic contributions of the gates:

\begin{enumerate}
    \item \textbf{Linear Coefficients (Diagonal Terms):} The diagonal elements $Q_{ii}$ represent the improvement (or degradation) a single gate provides relative to the baseline:
    \begin{equation}
        Q_{ii} = L_{\emptyset} - (M_{KL})_{ii}
    \end{equation}
    
    \item \textbf{Quadratic Coefficients (Off-Diagonal Terms):} For any pair of gates $\{G_i, G_j\}$, the physical circuit must adopt a specific temporal order. To simplify the optimization, we assume the solver utilizes the optimal ordering. We first define the best-order cost:
    \begin{equation}
        L_{best}(i,j) = \min \left( (M_{KL})_{ij}, (M_{KL})_{ji} \right)
    \end{equation}
    The interaction term $Q_{ij}$ is then derived by subtracting the individual costs from the joint cost to isolate the synergy:
    \begin{equation}
        Q_{ij} = (L_{best}(i,j) - L_{\emptyset}) - Q_{ii} - Q_{ij}
    \end{equation}
\end{enumerate}

Any sequence that results in an infinite or non-computable KL divergence is assigned a penalty $P \gg |Q_{ij}|_{max}$ to ensure the solver avoids invalid gate configurations.



\subsection{Stage 2: Variational Quantum Solution}
The QUBO is converted to an Ising Hamiltonian, whose ground state (the optimal gate set) is found using VQE or QAOA.
\begin{itemize}
    \item \textbf{VQE:} We use an \texttt{EfficientSU2} ansatz with a classical COBYLA optimizer to find the ground state.
    \item \textbf{QAOA:} As a comparison, we use a standard QAOA implementation, also with a COBYLA optimizer.
\end{itemize}
The output of the quantum solver is a probability distribution over possible solutions. We take the top-k most probable bitstrings as candidate solutions.

\subsection{Stage 3: Hybrid Post-Processing}
The quantum solver provides an optimal \textit{set} of gates, but not their order. For each of the top-k gate sets identified, we perform a final classical search to find the optimal permutation. This search is conducted using our \textbf{Multi-Epoch Sequential Construction (Algorithm 2)}, which efficiently finds a high-quality ordering for the small, promising set of gates selected by the quantum algorithm. The best sequence found across all top-k VQE solutions is chosen as the final topology.

\section{Spatial Mechanistic Simulation Framework}
\label{appendix:spatial_sim_cells}

To benchmark the quantum information-theoretic algorithm's ability to resolve directional causality, we developed a synthetic tissue framework that explicitly separates spatial signaling from intracellular regulation.

\subsection{Spatial Architecture and Interaction Kernel}
The tissue comprises $N$ cells $\mathcal{C}$ with spatial coordinates $P_i \in \mathbb{R}^2$. Intercellular connectivity is governed by a Gaussian decay kernel:
\begin{equation}
W_{ij} = \exp\left( -\frac{\|P_i - P_j\|^2}{2\sigma^2} \right), \quad i \neq j
\end{equation}
Cells are partitioned into four scenarios: \textit{Interacting Pairs} (A and B clusters within signaling range), \textit{Lone Senders} ($A_{lone}$), and \textit{Lone Receivers} ($B_{lone}$). This setup allows for the evaluation of algorithm robustness against spatial co-occurrence false positives.



\subsection{The Latent Manifold and Causality Chain}
The simulation models a continuous latent state $\mathbf{x}_i \in \mathbb{R}^G$ representing log-transformed transcriptomic potential. Every gene is initialized at a stochastic baseline $\bar{x}_{g,i} \sim \mathcal{N}(\mu_0, \sigma_{noise})$, where $\mu_0 = -2.0$ represents ``Biological Zero.'' Causality advances through a rigid temporal sequence:

\begin{enumerate}
    \item \textbf{Ligand Activation:} Sender cell ligands $x_{l,j}$ are manually shifted upward from baseline to represent active signal secretion.
    \item \textbf{Intercellular Signaling ($S_{r,i}$):} Receiver cell $i$ integrates neighbor signals by bridging the source expression ($x_{l,j}$) and induced response ($x_{r,i}$):
    \begin{equation}
    x_{r,i} = \bar{x}_{r,i} + \log\left( 1 + \alpha \sum_{j \in \mathcal{C}_{sender}} W_{ij} \cdot \exp(x_{l,j}) \right)
    \end{equation}
    \item \textbf{Intracellular GRN Propagation:} Downstream targets respond to the receptor via a Gene Regulatory Network (GRN) adjacency matrix $A_{gk}$:
    \begin{equation}
    x_{g,i} = x_{g,i} + \sum_{k \in \mathcal{G}} A_{gk} \cdot (x_{k,i} - \mu_0) \cdot \mathbb{I}(x_{k,i} > \tau)
    \end{equation}
    By subtracting $\mu_0$, we ensure the network responds only to relative activation (the ``shout'') while ignoring baseline stochasticity (the ``hum'').
\end{enumerate}

\subsection{Causal Benchmarking Scenarios}\label{appendix:lr_grn_benchmark}
We implement two distinct circuits to challenge the algorithm's resolution:
\begin{itemize}
    \item \textbf{Feedback Loop:} A three-stage intercellular circuit:
    \begin{equation}\label{appendix:lr_activation_path}
    \underbrace{50_{L} \xrightarrow{W_{ij}} 60_{R}}_{\text{Forward Signaling}} \implies \underbrace{60 \to 70 \to \{71, 72, 80_{L}\}}_{\text{Reactive GRN}} \implies \underbrace{80_{L} \xrightarrow{W_{ji}} 90_{R}}_{\text{Retrograde Feedback}}.
    \end{equation}
    \item \textbf{Autonomous Module:} An independent module ($73 \to \{74, 75\}$) initialized globally to test the decoupling of spatial information from intrinsic mutual information.
\end{itemize}



\subsection{Measurement Model and Sparsity}
To simulate technical capture inefficiency, the latent manifold is projected into observed UMI counts $Y_{gi}$ via a Negative Binomial distribution with Bernoulli-mask dropout:
\begin{equation}
Y_{gi} \sim \text{NB}\left(\exp(x_{gi}), \phi\right) \cdot \text{Bernoulli}(1 - \pi)
\end{equation}
With $\pi = 0.4$, the environment features $\sim 90\%$ sparsity, forcing the algorithm to distinguish biological signal from technical noise.

\noindent\textbf{Implementation Note:} The complete Python source code is available at \href{https://github.com/cailab-tamu/QuantumXCT/tree/main/python/simCellsSpace}{github.com/cailab-tamu/QuantumXCT/python/simCellsSpace}.

\end{appendices}


\bibliography{sn-bibliography}% common bib file
%% if required, the content of .bbl file can be included here once bbl is generated
%%\input sn-article.bbl


\end{document}
