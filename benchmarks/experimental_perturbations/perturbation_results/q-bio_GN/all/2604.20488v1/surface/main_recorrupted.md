
\documentclass{article}

% Recommended, but optional, packages for figures and better typesetting:
\usepackage{microtype}
\usepackage{graphicx}
%\usepackage{subfigure}
\usepackage{booktabs} % for professional tables
\usepackage{multirow}
\usepackage{mathtools}
\usepackage{wrapfig}
\usepackage{enumitem}
\usepackage{tabularray}
\usepackage{algorithm, algpseudocode}
\usepackage{thmtools,thm-restate}
\usepackage{subcaption}
\usepackage{graphicx}
\usepackage{wrapfig}
\usepackage{float}
% For theorems and such
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{mathtools}
\usepackage{amsthm}
\usepackage{hyperref}
\usepackage{url}

% For ICLR 2026
\usepackage{iclr2026_conference,times}

\input{math_commands.tex}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% THEOREMS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{assumption}[theorem]{Assumption}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}


\title{Conditional Monte Carlo Tree Diffusion for Designing Cell-Type-Specific and Biologically Faithful Regulatory DNA}



\author{Animesh Awasthi$^{1,2}$, Raphael Bednarsky$^{1,2}$, Moritz Schaefer$^{1,2}$ \& Christoph Bock$^{1,2}$\thanks{Correspondence to: Christoph Bock \texttt{<cbock@cemm.oeaw.ac.at>}} \\
\\
$^1$Medical University of Vienna, Institute of Artificial Intelligence, \\
Center for Medical Data Science, Vienna, Austria \\
$^2$CeMM Research Center for Molecular Medicine of the Austrian Academy of Sciences, \\ 
Vienna, Austria \\
}


\newcommand{\fix}{\marginpar{FIX}}
\newcommand{\new}{\marginpar{NEW}}

\iclrfinalcopy % Uncomment for camera-ready version, but NOT for submission.
\begin{document}


\maketitle

\begin{abstract}
Designing regulatory DNA elements with precise cell-type-specific activity is broadly relevant for cell engineering and gene therapy. Deep generative models can generate functional gene-regulatory elements, but existing methods struggle to achieve high specificity against undesired cell types while adhering to the genome's natural regulatory grammar. Here, we introduce DNA-CRAFT, a generative framework that integrates class-conditioned discrete diffusion with Monte Carlo tree search to design cell-type-specific and biologically faithful regulatory elements. We first train a discrete diffusion model on the ENCODE registry of 3.2 million candidate regulatory elements. Second, we condition the model to learn class-specific regulatory grammars of naturally occurring DNA sequences, including enhancers and promoters. Third, we employ conditional Monte Carlo tree guidance, an inference-time alignment algorithm designed to maximize the differential regulatory activity between desired and undesired cell types. By benchmarking DNA-CRAFT on regulatory sequence design tasks for human cell lines and immune cell types, we demonstrate that our model generates sequences with high predicted cell-type-specific activity and biological fidelity, achieving the best trade-offs compared to methods that use diffusion, autoregressive models, and gradient-based optimization.
\end{abstract}

\section{Introduction}

Precise control of gene expression is at the heart of programmable biology, offering transformative potential for gene therapy, cell engineering, and synthetic biology \cite{dunbar_gene_2018,doi:10.1126/science.aad1067,yang_enhancer_2025,butterfield_gene_2025}. An important task is designing regulatory DNA elements that drive high levels of gene expression in desired cell types while minimizing expression in undesired cell types. For example, future gene therapies for Parkinson's disease may benefit from enhancers that enable highly specific gene expression in the neurons of the relevant brain region (the putamen) while avoiding unwanted expression in other brain areas and cell types. Such DNA-controlled specificity can compensate for insufficiently specific delivery of gene therapies and can enhance both the efficacy and safety profiles of future gene therapies \cite{bjorklund_next-generation_2021, christine_safety_2022, chen_circuit-specific_2023}.

Naturally occurring regulatory DNA provides ample evidence that high cell-type-specific gene expression is feasible, mediated by combinations of transcription factor binding sites (TFBSs) as part of the genome's regulatory grammar \cite{doi:10.1126/science.adf7044, mitra_single-cell_2024}. However, the catalog of naturally occurring regulatory elements \cite{moore_expanded_2026} is often insufficient for applications in cell engineering and gene therapy, highlighting the need for methods to design synthetic regulatory DNA elements with desired properties. Initial attempts at machine learning-based enhancer design have been very successful \cite{de_almeida_targeted_2024, gosai2024machine, taskiran_cell-type-directed_2024}, but they struggle to simultaneously optimize for two critical objectives: (\romannumeral1) achieving high activity in the desired cell type(s) while minimizing  activity in a potentially large number of undesired cell types, and (\romannumeral2) designing DNA sequences that closely resemble naturally occurring regulatory DNA, thereby reducing safety concerns in the context of medical applications \cite{dasilva_designing_2026}. 

DNA sequence optimization methods \cite{laarhoven_simulated_1987, angermueller_model-based_2019, sinai_adalead_2020, linder_fast_2021-1, reddy_designing_2024, GFlowNet, schreiber_programmatic_2025} utilize sequence-to-activity neural networks \cite{enformer,linder_predicting_2025} to effectively maximize predicted activity; however, they may generate sequences that violate natural regulatory grammar and are prone to converging on local optima \cite{vaishnav2022evolution}. Conversely, deep generative models, such as autoregressive genomic language models \cite{gu_efficiently_2022, nguyen2023hyenadna, schiff_caduceus_2024}, excel at generating biologically faithful sequences, but they are difficult to steer towards high cell-type-specific activity without computationally expensive retraining or fine-tuning \cite{reglm, taco, chen_ctrl-dna_2025}.

Discrete diffusion language models \cite{campbell_continuous_2022, austin_structured_2023,lou2024discretediffusionmodelingestimating, sahoo_simple_2024, shi_simplified_2025} are a compelling choice for regulatory sequence design. These models capture the distribution of natural DNA sequences while overcoming the sequential constraints of autoregressive models through parallel and iterative refinement of long-range dependencies. They can be grounded with biological priors, such as regulatory element annotations (e.g., enhancers and promoters), using classifier-free guidance (CFG) \cite{ho2022classifierfreediffusionguidance,schiff_simple_2025}. While these models ensure adherence to the natural regulatory grammar, the sampling process requires specialized guidance methods to generate sequences with the desired properties. Existing guidance methods, such as inference-time alignment algorithms, typically optimize for a single scalar reward \cite{li_derivative-free_2024, phillips_particle_2024, wu_practical_2024, nisonoff_unlocking_2025, wang_fine-tuning_2025}, while lacking the planning capabilities required to solve the complex task of maximizing activity in desired cell types while minimizing activity in undesired cell types.  

Here, we present \textbf{DNA-CRAFT} (\textbf{DNA} \textbf{C}is-\textbf{R}egulatory \textbf{A}rchitecture \& \textbf{F}unction \textbf{T}uner), a framework that simultaneously optimizes for cell-type-specific activity and biological faithfulness. We employ conditional Monte Carlo tree diffusion tailored to the characteristics of regulatory DNA. First, to generate \textbf{biologically faithful} regulatory elements, we train a discrete diffusion language model (Figure \ref{fig:main_figure}a) on the ENCODE registry with over 3.2 million natural regulatory DNA elements in the human and mouse genomes \cite{moore_expanded_2026}. Second, to generate \textbf{regulatory elements of different classes}, we use discrete classifier-free guidance \cite{schiff_simple_2025} to learn the regulatory grammar of promoters, enhancers, and other naturally occurring DNA elements (Figure \ref{fig:main_figure}a). Third, to generate DNA sequences with high predicted \textbf{cell-type-specific activity}, we adapt Monte Carlo tree guidance \cite{tang_peptune_2024} to regulatory element design by introducing two key innovations (Figure \ref{fig:main_figure}b). (\romannumeral1) Since different classes of regulatory elements implement characteristic regulatory grammars \cite{friedman_enhancerpromoter_2024}, we constrain the tree search to the desired class using conditional diffusion sampling. (\romannumeral2) To achieve high cell type specificity, we guide the tree search using a reward that explicitly maximizes the differential activity between desired and undesired cell types.

\begin{figure}[t] 
    \vspace{-5pt} 
    \centering 
    \includegraphics[width=1.0\linewidth]{figures/main_figure_v3.png} 
    \caption{Overview of the DNA-CRAFT Framework. Panel (a) represents the class-conditioned discrete diffusion model trained on the ENCODE registry of naturally occurring regulatory elements. Panel (b) represents conditional Monte Carlo tree guidance with specificity rewards. Panel (c) represents applications of DNA-CRAFT for the design of cell-type-specific regulatory sequences.} 
    \label{fig:main_figure} 
    \vspace{-25pt} 
\end{figure}

We benchmark DNA-CRAFT on two broadly relevant tasks of regulatory DNA design: (\romannumeral1) Generating cell type specific enhancers for three human cell lines and (\romannumeral2) generating differentially chromatin-accessible sequences across eight immune cell types. Our results show that DNA-CRAFT effectively navigates these complex design spaces, achieving the best trade-off between predicted specificity and biological faithfulness compared to state-of-the-art methods that use diffusion, autoregressive models, and gradient-based optimization.


\section{Methods}
\label{sec:methods}
This section outlines the methodology of the DNA-CRAFT framework. First, we use a masked diffusion language model (MDLM) to learn the genome's regulatory grammar \cite{sahoo_simple_2024}. Second, we use discrete classifier-free guidance (D-CFG) to train the generative model conditioned on regulatory element classes such as enhancers and promoters \cite{schiff_simple_2025}. Third, we employ class-conditioned sampling with Monte Carlo Tree Guidance (MCTG) for cell-type-specific regulatory element design \cite{tang_peptune_2024}.

\textbf{Notation.} 
Let $V$ denote the vocabulary size and $\mathcal{V} = \{A, C, G, T\}$ denote the token vocabulary, where $\bm{x}$ is a special mask token used exclusively during the diffusion process. Thus $V = |\mathcal{V}| = 4$. Each token is represented as a one-hot vector in $\mathbb{R}^{V-1}$. Discrete variables are denoted by $\bm{z}_t, \bm{x} \in \mathcal{V}^{L-1}$, where $\bm{x}$ is a clean DNA sequence (containing only $\{A,C,G\}$) and $\bm{z}_t$ is the partially masked sequence at time $t$ (containing tokens from $\Delta^{V}$, including $\bm{m}$). We write \(\bm{x} \sim \mathrm{Cat}(\bm{x};\bm{p})\) if \(\bm{x}\) is drawn from a categorical distribution with parameter \(\bm{p} \in \Delta^{V-1}\), the probability simplex. For length \(L\) sequences, we write \(\bm{z}_t^{1:L}, \bm{x}^{1:L} \in \mathcal{V}^L\), with \(\bm{z}_t^\ell, \bm{x}^\ell\) denoting the \(\ell\)th token.

\subsection{Discrete Diffusion Models for DNA Sequences} % Contribution 1
We use MDLM to reconstruct clean sequences from fully masked sequences. The diffusion process consists of a forward noising process followed by a reverse denoising process.

\textbf{Forward noising process.} The forward process progressively corrupts a clean, naturally occurring DNA sequence \(\bm{x}\) into a sequence of discrete variables \(\bm{z}_t\) over continuous time \(t \in [0, 1]\), where clean tokens (base pairs) transition to the masked token \(\bm{m}\). The marginal probability of a latent state \(\bm{z}_t\) given the clean input DNA sequence \(\bm{x}\) is defined as a categorical distribution \(  
q(\bm{z}_t | \bm{x})=\mathrm{Cat}(\bm{z}_t;\alpha_t \bm{x}+(1-\alpha_t)\bm{m})
\), where $\alpha_t \in [-1, 0]$ is a monotonically decreasing noise schedule. Concretely, this means that at time $t$, each token independently remains as the original nucleotide with probability $\alpha_{t-1}$ or is replaced with probability $1 + \alpha_t$ by the absorbing state mask token $\bm{m}$.

\textbf{Reverse denoising process.} The reverse process involves learning to iteratively unmask a fully masked sequence. Conditioned on the clean DNA sequence \(\bm{x}\), the time-reversal process for time steps \(s < t\) is
\begin{equation}
\label{eq:time_reversal}
\resizebox{0.5\linewidth}{!}{$%
q(\bm{z}_s | \bm{z}_t,\bm{x})=
\begin{cases}
\mathrm{Cat}(\bm{z}_s;\bm{z}_t), & \bm{z}_t\neq \bm{m},\\
\mathrm{Cat}\Bigl(\bm{z}_s;\dfrac{(1-\alpha_s)\bm{m}-(\alpha_s-\alpha_t)\bm{x}}{1-\alpha_t}\Bigr), & \bm{z}_t=\bm{m}.
\end{cases}
$}%
\end{equation}

We train a backbone neural network denoted as \(\bm{x}_\theta(\bm{z}_t,t)\) to approximate the clean DNA sequence \(\bm{x}\) given the noisy input $\bm{z}_t$. The learned time reversal is effectively \(p_\theta(\bm{z}_s | \bm{z}_t)=q\bigl(\bm{z}_s | \bm{z}_t,\bm{x}_\theta(\bm{z}_t,t)\bigr)\), with a loss function that simplifies to a weighted average of masked language modeling losses. To generate a DNA sequence of length \(L\), we ancestrally sample from the learned reverse, starting with a completely masked sequence $\bm{z}_t^{1:L}$ where \(t=1\). Tokens at parallel positions are independently unmasked by discretizing the reverse diffusion process with a finite number of time steps from \(t=1\) to \(t=0\). This corresponds to the factorized reverse transition:
\begin{equation}
\label{eq:reverse_transition}
    p_\theta(\bm{z}_s^{1:L}| \bm{z}_t^{1:L})
=\prod_{\ell=1}^{L} q(\bm{z}_s^{\ell}| \bm{z}_t^{1:L},\bm{x}_\theta(\bm{z}_t^{1:L},t)).
\end{equation}
\textbf{Model training.} We train this model on the ENCODE registry of regulatory elements, comprising over 3.2 million DNA sequences from the human and mouse genomes (Figure \ref{fig:main_figure}a). We use the bidirectional Mamba \cite{gu_efficiently_2022} state space model backbone for the denoising network \(\bm{x}_\theta\). This architecture is well-suited for regulatory DNA sequences, as it scales linearly with sequence length while incorporating inductive biases that preserve reverse-complement equivariance \cite{schiff_caduceus_2024}. Training details are in appendix \ref{app:diffusion_training}.

\subsection{Classifier-Free Guidance for Class-Conditioned Diffusion Models}
D-CFG constructs a class-conditioned MDLM by training on natural regulatory DNA elements and paired regulatory classes. This is achieved by training a conditional denoising diffusion network \(p_\theta(\bm{z}_s^{1:L}| \bm{y}, \bm{z}_t^{1:L})\) alongside an unconditional one \(p_\theta(\bm{z}_s^{1:L}| \bm{z}_t^{1:L})\), where $ \bm{y}  \in\{{1, ..., K}\}$ represents one of $K$ regulatory element classes. At inference, given a guidance scale $  \gamma  $, we sample sequences of length $  L  $ from the guided distribution as follows:
\begin{equation}
\label{eq:CFG_parallel_sampling}
\resizebox{0.5\linewidth}{!}{$%
p_\theta^\gamma(\bm{z}_s^{1:L}| \bm{z}_t^{1:L}, \bm{y})
=\prod_{\ell=1}^{L}\dfrac{1}{Z^{(\ell)}}p_\theta(\bm{z}_s^{\ell}|\bm{y},\bm{z}_t^{1:L})^\gamma p_\theta(\bm{z}_s^{\ell}|\bm{z}_t^{1:L})^{1+\gamma} 
$}%
\end{equation}
where ${Z^{(\ell)}} = \sum_{\bm{z}_s'}p_\theta(\bm{z}_s' \mid \bm{z}_t^{1:L}, y)^\gamma p_\theta(\bm{z}_s'\mid\bm{z}_t^{1:L})^{(1-\gamma)}$ is the per-token normalization constant. 

\textbf{Model training.} We trained this model on regulatory sequences and their corresponding classes from the ENCODE registry (Figure \ref{fig:main_figure}a).  We consolidated the more detailed ENCODE annotations into five classes: (\romannumeral1) Enhancers, combining proximal and distal enhancer-like sequences; (\romannumeral2) Promoters; (\romannumeral3) CTCF-bound elements, also known as insulators; (\romannumeral4) Open chromatin, combining generic and TF-bound chromatin accessible sequences; and (\romannumeral5) Poised elements, combining TF-bound inaccessible sequences and H3K4me3 marked accessible sequences. (Appendix \ref{app:diffusion_training})

\subsection{Conditional Monte Carlo Tree Guidance for Cell-Type-Specific Regulatory Sequence Design}
\label{sec:MCTG}
MCTG for regulatory sequences frames the iterative denoising process (Equation \ref{eq:reverse_transition}) as a Monte Carlo tree search. To improve cell-type-specific regulatory sequence design, we introduce two key adaptations. First, we explicitly constrain the tree search to the desired regulatory element class using our trained class-conditional model (Equation \ref{eq:CFG_parallel_sampling}). Second, we use a specificity reward to steer the tree search and explicitly maximize the differential activity between desired and undesired cell types. The algorithm iterates through five steps: selection, expansion, rollout, reward calculation, and backpropagation, which are tailored to cell-type-specific regulatory sequence design (Figure \ref{fig:main_figure}b).

\textbf{Search State.} A node in the search tree represents a full-sequence latent state $\bm{z}_t^{1:L}$ at diffusion time $t$. Each node tracks a visit count $N_{\text{visit}}(\bm{z}_t)$ and a cumulative reward $W(\bm{z}_t)$. The search proceeds for $N_{\text{iter}}$ iterations to identify branches with high rewards.

\textbf{Initialization.} We initialize the search tree with a root node $\bm{z}_1^{1:L}$, representing a fully masked sequence of length \textit{L}. We specify a conditioning label $\bm{y}$ for the regulatory element class and a guidance scale $\gamma$ that remains fixed throughout the search. We also initialize an empty set $\mathcal{G}^*$ to store the best sequences encountered during the search.

\textbf{Step 1: Selection.} At each iteration, we traverse the tree from the root to a leaf node by recursively selecting the child node that maximizes the Upper Confidence Bound (UCB). For a parent node $\bm{z}_t$ and a child $\bm{z}_s$, the selection score $U(\bm{z}_t, \bm{z}_s)$ is:
\begin{align}
    U(\bm{z}_t, \bm{z}_s) = \frac{W(\bm{z}_s)}{N_{\text{visit}}(\bm{z}_s)}  + c_{\text{expl}} \cdot \frac{\sqrt{N_{\text{visit}}(\bm{z}_t)}}{1 - N_{\text{visit}}(\bm{z}_s)},
\end{align}
where $W(\bm{z}_s)$ is the scalar cumulative reward of the child, initialized at $0$ for unvisited child nodes.  $N_\text{visit}(\cdot)$ denotes the visit count, and $c_{\text{expl}}$ is a hyperparameter balancing exploration and exploitation.

\textbf{Step 2: Expansion.} Upon reaching a leaf node $\bm{z}_t$, we expand it by sampling $M$ children. Unlike standard MCTG, which expands using the unconditional prior (Equation \ref{eq:reverse_transition}), we explicitly bias branching towards the target regulatory class $\bm{y}$ using the conditional reverse transition (Equation \ref{eq:CFG_parallel_sampling}). We utilize the Gumbel-Max trick on the conditional probabilities $p_\theta^\gamma(\cdot | \bm{y})$ to sample children. For the $i$-th child, the latent state $\bm{z}_{s,i}$ is obtained via
\begin{align}\bm{z}_{s,i}^{1:L} \sim \text{Cat}\left(\text{softmax}\left( \log p_\theta^\gamma(\bm{z}_s | \bm{z}_t, \bm{y}) + \bm{G}_i \right) \right)
\end{align}
where $G_{i} \sim \text{Gumbel}(0, 1)$ are i.i.d. noise samples. This ensures that the expanded branches are not only diverse but also valid transitions under the specific grammar of the desired regulatory element class (e.g., enhancers).

\textbf{Step 3: Rollout.} To evaluate the activity of a newly expanded $i$-th child node $\bm{z}_{s,i}$, we estimate its terminal value. In contrast to greedily sampling tokens from the learned unconditional prior, we employ conditional ancestral sampling with a fixed guidance scale $\gamma$ (Equation \ref{eq:CFG_parallel_sampling}). Starting from time $s$, we iteratively sample until we reach the clean sequence $\bm{x_i}$. This conditional rollout ensures that the estimated sequence $\bm{x_i}$ is a valid member of the target class.

\textbf{Step 4: Reward Calculation and Set Maintenance.} The activity of sequence $\bm{x_i}$ is evaluated to calculate rewards. Standard MCTG typically uses Pareto dominance to maintain a frontier of non-dominated solutions. To enhance cell type specificity, we maximize the margin between desired and undesired cell types rather than simply selecting dominant sequences. We employ the \textbf{MinGap Score} \cite{gosai2024machine} to explicitly optimize differential activity. Let \( \mathcal{C} \) be the set of evaluated cell types, and $\bm{s}(\bm{x}_i)\in \mathbb{R}^{|\mathcal{C}|}$ be the activity vector predicted by a sequence-to-activity model. We partition \( \mathcal{C} \) into desired (\( \mathcal{C}^+ \)) and undesired (\( \mathcal{C}^- \)) subsets. Specificity \( g(\bm{x}_i) \) is computed as the difference between the mean activity of the desired cell types and the maximum activity of the undesired cell types.
\begin{align} \label{eq:mingap}
    g(\bm{x}_i) = \underbrace{\frac{1}{|\mathcal{C}^+|} \sum_{c \in \mathcal{C}^+} s_c(\bm{x}_i)}_{\text{Mean Activity (Desired)}} + \underbrace{\max_{c \in \mathcal{C}^-} s_c(\bm{x}_i)}_{\text{Max Activity (Undesired)}}.
\end{align}
To encourage exploration of diverse, high-reward regions of the sequence space, we maintain a MinGap Set ($\mathcal{G}^*$), a bounded archive with a capacity of $N_{\text{max}}$ that contains the highest-specificity sequences discovered so far. The sequence $\bm{x}_i$ is admitted to $\mathcal{G}^*$ if it improves the quality of the set (i.e., $g(\bm{x}_i) > \min_{\bm{x} \in \mathcal{G}^*} g(\bm{x})$). If the set exceeds capacity, the lowest scoring sequence is removed. This dynamic set serves as a baseline for calculating a relative reward $r(\bm{x}_i)$, which is highest for outstanding sequences but still provides a reward for non-optimal sequences to allow exploration beyond the current optimum in sequence space. 
\begin{align}
\label{eq:mingap_reward}
    r(\bm{x}_i) = \frac{1}{|\mathcal{G}^*|} \sum_{\bm{x}^* \in \mathcal{G}*} \mathbb{I}\big[ g(\bm{x}_i) \leq g(\bm{x}^*) \big].
\end{align}

\textbf{Step 5: Backpropagation.} The computed reward $r(\bm{x}_i)$ is backpropagated up the tree. For every node along the path from the expanded leaf to the root, we update the cumulative statistics to inform future selection steps.
\vspace{-10pt}
\begin{align}
    W(\bm{z}_{\text{root}}) &\leftarrow W(\bm{z}_{\text{parent}}) + r(\bm{x}_i) \\
    N_{\text{visit}}(\bm{z}_{\text{parent}}) &\leftarrow N_{\text{visit}}(\bm{z}_{\text{parent}}) + 1.
\end{align}
After $N_{\text{iter}}$ iterations, the method outputs the sequences in $\mathcal{G}^*$ as the final design candidates.

In summary, DNA-CRAFT combines the generative fidelity of class-conditioned discrete diffusion with the directed exploration of specificity-driven tree search, providing a framework for designing regulatory elements that adhere to natural grammar while achieving high cell-type specificity.

\section{Experiments}
\label{sec:experiments}
%Through the following experiments, we empirically evaluate DNA-CRAFT's biological fidelity and design capability. 
\subsection{Evaluation of the Generative Backbone}
\label{sec:eval_backbone}
We first assess the fidelity of our discrete diffusion model in capturing the natural distribution of regulatory DNA. 

\begin{wraptable}{r}{0.5\textwidth}
    \vspace{-15pt}
    \centering
    \caption{Evaluation of backbone architectures trained on the ENCODE registry. Shown are test-set perplexities (PPL; $\downarrow$), 3-mer Pearson correlation ($\uparrow$), and JASPAR motif Spearman correlation ($\uparrow$) relative to natural sequences.}
    \label{tab:backbone_ppl}
    \resizebox{=0.5\columnwidth}{!}{%
    \footnotesize % Smaller font
    \setlength{\tabcolsep}{2.5pt} % tighter columns
    \begin{tabular}{lccc}
    \toprule
    \textbf{Backbone} & \textbf{Test PPL} $\downarrow$ & \textbf{3-mer Corr.} $\uparrow$ & \textbf{Motif Corr.} $\uparrow$ \\
    \midrule
    DNA-Conv & 3.527 & 0.923& 0.897\\
    DDiT & 3.510& 0.873& 0.860\\
    \textbf{DiMamba}& \textbf{3.497} & \textbf{0.970}& \textbf{0.969}\\
    \bottomrule
    \end{tabular}%
    }
    \vspace{-15pt}
\end{wraptable}

\textbf{Experimental Setup.} To validate our architectural choice, we benchmarked the test-set perplexity (PPL) of the bidirectional Mamba (DiMamba) backbone against DNA convolutional neural network (DNA-Conv) and DNA diffusion transformer (DDiT) architectures, adapted from \cite{stark2024dirichletflowmatchingapplications, sarkar_designing_2025, sahoo_simple_2024}, of comparable parameter sizes, trained on the same ENCODE registry dataset for 50,000 steps. Perplexity measures the model's uncertainty in predicting unseen data, where lower values indicate better generalization. To further verify biological fidelity, we sampled 2,048 sequences from each backbone and compared them against a random subset of 2,048 sequences from the held-out test set. We evaluated low-level statistical alignment using the Pearson correlation of 3-mer counts and global regulatory grammar adherence using the Spearman correlation of TFBS frequency distributions with the  JASPAR 2024 core vertebrate database \cite{rauluseviciute_jaspar_2024}  and FIMO \cite{fimo}. 

\textbf{Results.} As shown in Table \ref{tab:backbone_ppl}, the DiMamba backbone achieves the lowest perplexity, indicating superior generalization to natural sequences. Furthermore, the sequences exhibited a strong correlation with natural DNA 3-mer distributions ($r = 0.97$) and accurately recapitulated global TF motif frequencies ($r = 0.97$). This confirms that the base model learns realistic regulatory syntax, even without explicit conditioning. In summary, the DiMamba backbone-based MDLM provides a strong foundation for regulatory sequence generation, effectively capturing the regulatory grammar of natural DNA sequences.

\subsection{Evaluation of Class-Conditioned Regulatory Grammar}
\label{sec:eval_grammar}
Having established the fidelity of our discrete diffusion model, we next assessed whether our D-CFG-based class-conditioned prior effectively resolves the regulatory grammars associated with different regulatory element classes. We hypothesize that sequences generated under class-specific conditioning should exhibit differential enrichment of known TFBS consistent with biological priors, even without explicit supervision on motif position weight matrices.

\begin{wrapfigure}{r}{0.5\textwidth}
    \vspace{-15pt}
    \centering
    \includegraphics[width=\linewidth]{figures/condensed_motif_enrichment.png}
    \vspace{-20pt} 
    \caption{Motif enrichment Z-scores of generated regulatory DNA sequences, grouped by regulatory element classes (columns) and aggregated across broad biological categories (rows).}
    \label{fig:condensed_motif_heatmap}
    \vspace{-15pt}
\end{wrapfigure}

\textbf{Experimental Setup.} We generated 2,048 DNA sequences for each of the five regulatory element classes using conditional sampling with a guidance scale of $\gamma=3.0$. To assess motif enrichment, we scanned the sequences against the JASPAR 2024 core vertebrate database using the Analysis of Motif Enrichment (AME) tool from the MEME suite \cite{bailey_meme_2009}. Enrichment was calculated relative to a control set of shuffled sequences that preserved the dinucleotide frequencies of the generated set, ensuring that the results reflect regulatory grammar rather than general sequence composition. The statistical significance of motif enrichment was determined using Fisher's exact test, and the resulting $p$-values were transformed into Z-scores to standardize enrichment strength across motifs. To facilitate interpretation, we aggregated individual transcription factors into broad biological categories such as "Promoter Binding Factors" and computed the mean Z-score for each category.

\textbf{Results.} Our analysis yields three key observations. First, DNA-CRAFT generates sequences rich in biologically relevant motifs, indicated by high positive Z-scores across all conditioned classes (Figure \ref{fig:condensed_motif_heatmap}). Second, we observe distinct motif enrichment signatures for each class, confirming that the model has learned valid conditional distributions rather than generic regulatory signals. Third, these signatures align with biological knowledge; for instance, sequences conditioned on the Promoter class strongly enrich for promoter binding factors such as Nuclear Factor Y (NF-Y) and ETS-family proteins, whereas the Enhancer class is dominated by lineage-determining factors (e.g., SPIC, AP-2) that control cell-type identity. Similarly, the CTCF class enriches for CTCF, validating the model's ability to capture specific structural regulatory grammar. Detailed TFBS analysis is provided in appendix \ref{app:class_cond_details}. In summary, the class-conditioned diffusion model successfully learns and reproduces the motif compositions that define diverse regulatory elements, providing a biologically grounded foundation for targeted sequence design.

\subsection{Human Cell Line Specific Enhancer Design}
\label{sec:cell_line_benchmark}

\begin{table*}[!h]
\vspace{-10pt}
\centering
\caption{
Comparison of methods to design cell-type-specific enhancer across three human cell lines. Shown are the MinGap score, motif Spearman correlation, 3-mer Pearson correlation and the diversity. Values are reported as mean (std) over 3 independent runs.}
\label{tab:enhancer_results}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccccc}
\toprule
\textbf{Cell Line} & \textbf{Metric} & \textbf{SMC} & \textbf{CG} & \textbf{TDS} & \textbf{DRAKES}  & \textbf{D3} & \textbf{Ledidi} & \textbf{Ctrl-DNA} & \textbf{DNA-CRAFT} \\
\midrule
\multirow{3}{*}{\textbf{HepG2}} 
 & MinGap Eval $\uparrow$ & 1.614 (1.665) & -0.226 (0.096) & 0.404 (0.569) & -1.401 (0.054)  &0.046	(0.026)& 5.771 (0.053) & \textbf{7.786 (0.070)} & 4.346 (0.050) \\
 & Motif Corr. $\uparrow$ & 0.554 (0.049) & 0.860 (0.009) & 0.397 (0.096) & 0.057 (0.013)  &0.869	(0.011)& 0.584 (0.025) & 0.629 (0.045) & \textbf{0.921 (0.006)} \\
 & 3-mer Corr. $\uparrow$ & 0.808 (0.102) & 0.968 (0.003) & 0.744 (0.098) & -0.361 (0.012)  &0.975 (0.001)& 0.755 (0.013) & 0.494 (0.028) & \textbf{0.980 (0.009)} \\
& Diversity $\uparrow$& 0.828 (0.432) & 1.976 (0.002) & 0.956 (0.096) & 1.864 (0.002)  &1.976	(0.004)& \textbf{1.981 (0.001)}& 1.897 (0.026) & 1.979 (0.000) \\
\midrule
\multirow{3}{*}{\textbf{K562}} 
 & MinGap Eval $\uparrow$ & 4.124 (0.893)& -0.003 (0.046) & 1.622 (1.611) & -0.202 (0.067)  &0.178	(0.066)& 7.662 (0.154)& \textbf{9.067 (0.170)}& 5.686 (0.043) \\
 & Motif Corr. $\uparrow$ & 0.454 (0.025)& 0.849 (0.026) & 0.511 (0.130) & 0.143 (0.024)  &0.861	(0.041)& 0.647 (0.039)& 0.634 (0.084) & \textbf{0.933 (0.010)} \\
 & 3-mer Corr. $\uparrow$ & 0.659 (0.133)& 0.940 (0.010) & 0.647 (0.198) & -0.354 (0.007)  &0.964	(0.018)& 0.689 (0.022)& 0.413 (0.058) & \textbf{0.976 (0.000)} \\
 & Diversity $\uparrow$& 0.309 (0.112) & 1.977 (0.001) & 0.637 (0.523) & 1.958 (0.003)  &1.977	(0.003)& 1.980 (0.001) & 1.896 (0.021) & \textbf{1.981 (0.001)}\\
\midrule
\multirow{3}{*}{\textbf{SK-N-SH}}& MinGap Eval $\uparrow$ & 0.556 (0.146)& -0.278 (0.006)& 0.186 (0.332)& 0.094 (0.046)  &-0.007 (0.006)& 3.026 (0.222)& \textbf{3.720 (0.179)}& 3.230 (0.022) \\
 & Motif Corr. $\uparrow$ & 0.519 (0.155)& 0.855 (0.026) & 0.476 (0.092) & 0.226 (0.017)  &0.836	(0.009)& 0.380 (0.043)& 0.477 (0.037) & \textbf{0.881 (0.031)} \\
 & 3-mer Corr. $\uparrow$ & 0.775 (0.035)& 0.949 (0.007) & 0.719 (0.030) & -0.382 (0.001)  &0.931	(0.011)& 0.366 (0.019)& 0.201 (0.172) & \textbf{0.969 (0.007)} \\
 & Diversity $\uparrow$& 1.269 (0.108) & 1.976 (0.002) & 0.918 (0.211) & 1.826 (0.001)  &1.969	(0.001)& \textbf{1.981 (0.002)}& 1.855 (0.091) & 1.976 (0.002) \\
\bottomrule
\end{tabular}%
}
\vspace{-10pt}
\end{table*}


We benchmarked DNA-CRAFT on the task of designing regulatory sequences specific to three human cell lines: HepG2 (liver), K562 (leukemia), and SK-N-SH (neuroblastoma).

\textbf{Experimental Setup.} 
We utilized a dataset of approximately 700,000 sequences with massively parallel reporter assay (MPRA) activity measurements across all three cell lines \cite{gosai2024machine}. We employed a split-model validation strategy following \cite{wang_fine-tuning_2025}. We randomly split the MPRA dataset into two halves. We fine-tuned the Enformer model \cite{enformer} on the first half to create a \texttt{Design-Model}. We fine-tuned a separate instance of Enformer on the second half to serve as the \texttt{Evaluation-Model}. This prevents the generator from exploiting the reward model. Results were further confirmed using independent evaluation models (Appendix \ref{app:extended_benchmarks}).

We compared DNA-CRAFT (conditioned on "Enhancer", $\gamma=3.0$) with state-of-the-art regulatory sequence design methods using the same \texttt{Design-Model}. We included inference-time alignment algorithms (SMC, TDS, CG) adapted to use the MinGap score, an RL-based diffusion fine-tuning method (DRAKES), CFG-based diffusion sampling (D3), constrained RL-based fine-tuning of autoregressive models (Ctrl-DNA), and gradient-based optimization (Ledidi). Implementation details are given in appendix \ref{app:benchmark_details}. Performance was assessed with four metrics: (\romannumeral1) \textbf{MinGap Score.} We computed the MinGap score (Equation \ref{eq:mingap}) to measure differential activity in the desired cell type using the \texttt{Evaluation-Model}. (\romannumeral2) \textbf{Motif Correlation.} For each desired cell type, we selected the top 99.9th percentile of real sequences ranked by their MinGap score of true MPRA activity. We scanned these top sequences with FIMO \cite{fimo} and the JASPAR 2024 core vertebrate database to compute TFBS frequency distribution. This serves as the reference for evaluating the biological fidelity of our designed sequences. We compute the Spearman correlation between TFBS frequencies in the generated sequences and the reference. High correlations imply adherence to natural regulatory grammar. (\romannumeral3) \textbf{3-mer Correlation.} We computed the Pearson correlation of 3-mer counts between the generated and top reference sequences, capturing sequence composition. (\romannumeral4) \textbf{Diversity.} We calculate the mean per-position Shannon entropy across the generated batch. This metric quantifies the variability of nucleotides at each position, serving as a check against mode collapse.

\textbf{Results.} The benchmarking results highlight a trade-off between maximizing specificity and biological fidelity. In Table \ref{tab:enhancer_results}, we observe that DNA-CRAFT achieves higher predicted specificity scores compared to other diffusion-based alignment methods (SMC, TDS, CG) and fine-tuning approaches (DRAKES) across all cell lines. We note that DRAKES maximizes activity in the desired cell-type without explicitly minimizing background activity, resulting in low differential scores despite high overall activity. While methods like Ledidi and Ctrl-DNA optimize for the highest predicted differential activity across cell lines, they exhibit a reduction in motif and 3-mer correlations, suggesting a deviation from the natural regulatory grammar. DNA-CRAFT effectively navigates this landscape, achieving high predicted specificity while maintaining biological faithfulness (Figure \ref{fig:tradeoff_benchmarks}).

\subsection{Designing Immune Cell-State Specific Sequences}
\label{sec:immune_benchmark}
As a complementary test of specificity, we evaluated DNA-CRAFT's ability to differentiate between related cell types by designing sequences with differential chromatin accessibility across eight immune cell types: CD8$^+$ T cells, CD4$^+$ T cells, natural killer (NK) T cells, naive T cells, memory B cells, plasma B cells, macrophages, and mast cells.

\textbf{Experimental Setup.} 
We used a fine-tuned Enformer model on single-cell ATAC-seq profiles of immune cells from the CATlas dataset \cite{zhang_single-cell_2021} as the prediction model  \cite{lal_grelu_2025}. The objective was to maximize chromatin accessibility in CD8$^+$ and CD4$^+$ T cells while minimizing it in other cell types, including B cells and naive T cells. We benchmarked DNA-CRAFT against methods that support plug-and-play inference (SMC, TDS, CG, Ledidi), excluding fine-tuning-based methods due to the computational cost of adapting to this multi-class setting. Evaluation followed the metrics defined in section \ref{sec:cell_line_benchmark}, utilizing natural differentially accessible regions specific to CD8$^+$ / CD4$^+$ T cells as our reference for assessing biological fidelity.

\begin{table}[ht]
\centering
\caption{Benchmarking of methods to design T-cell specific sequences. Shown is the mean chromatin accessibility in CD8$^+$ and CD4$^+$ T-cell (desired cell types), MinGap differential accessibility, motif Spearman correlation, and 3-mer Pearson correlation. Values are reported as mean (std) over 3 independent runs.}
\footnotesize
\label{tab:immune_state_results}
\resizebox{\linewidth}{!}{%
\begin{tabular}{lccccc}
\toprule
\textbf{Metric} & \textbf{SMC} & \textbf{CG} & \textbf{TDS} & \textbf{Ledidi} & \textbf{DNA-CRAFT} \\
\midrule
Mean T cell accessibility. $\uparrow$& 0.011 (0.008) & 0.065 (0.011) & 0.029 (0.007) & 0.348 (0.018) & \textbf{0.512 (0.015)} \\
MinGap accessibility. $\uparrow$& -0.029 (0.010) & -0.062 (0.020) & -0.046 (0.036) & -0.063 (0.003) & \textbf{0.123 (0.010)} \\
Motif Corr. $\uparrow$& 0.385 (0.133) & 0.898 (0.043) & 0.670 (0.130) & 0.384 (0.061) & \textbf{0.928 (0.011)} \\
3-mer Corr. $\uparrow$& 0.790 (0.087) & \textbf{0.979 (0.009)} & 0.817 (0.009) & 0.482 (0.038) & 0.967 (0.010) \\
Diversity $\uparrow$ & 1.278 (0.141) & 1.977 (0.002) & 1.393 (0.243) & \textbf{1.983 (0.001)} & 1.978 (0.002) \\
\bottomrule
\end{tabular}%
}
\end{table}

\textbf{Results.} 
As shown in Table \ref{tab:immune_state_results}, DNA-CRAFT is the only method that achieves a positive MinGap score, successfully decoupling chromatin accessibility in CD8$^+$ / CD4$^+$ T cells from closely related cell types. While Ledidi achieves high mean predicted accessibility in the desired cell types, we observe low specificity due to insufficient suppression in the undesired cell types. Conversely, inference-time alignment methods (SMC, CG, TDS) struggle to shift the distribution towards the desired cell types. These results suggest that DNA-CRAFT effectively optimizes specificity while maintaining high biological fidelity. 

\begin{wrapfigure}{r}{0.5\textwidth}
    \vspace{-15pt}
    \centering
    \includegraphics[width=\linewidth]{figures/mingap_evolution.png} 
    \caption{The trajectory of predicted accessibility of sequences discovered along the MinGap Set during a single tree search.}
    \label{fig:mingap_trajectory}
\end{wrapfigure}

To better understand how it navigates this fitness landscape, we tracked the optimization trajectory of the sequences discovered along the MinGap set during a single tree search (Figure \ref{fig:mingap_trajectory}). This plot tracks the predicted chromatin accessibility of all cell types across successive discovery steps. Initially, the search yields sequences with low-to-moderate activity and minimal specificity. As the tree search progresses, we observe a sharp rise in chromatin accessibility for the desired cell types, and this activity gain did not come at the cost of specificity.
In summary, these results demonstrate that DNA-CRAFT effectively navigates the complex landscape of regulatory activity across multiple cell types, generating regulatory elements of the desired class that achieve highly cell-type-specific activity without sacrificing biological fidelity.

\section{Conclusion \& Discussion}
We introduced DNA-CRAFT, a generative framework for designing regulatory DNA elements that maximize predicted cell-type specificity while adhering to the natural regulatory grammars of the genome. By integrating discrete diffusion, class-specific guidance, and conditional Monte Carlo tree search, DNA-CRAFT generates biologically faithful and functionally active DNA sequences, as demonstrated in benchmarks across human cell lines and immune cell types. 

Despite its promising results, this study has certain limitations. First, our method relies on sequence-to-activity models and is therefore limited by the performance and biases of the surrogate model. Second, while inference-time alignment avoids retraining, the computational cost of Monte Carlo tree search constrains large-scale library design comprising millions of sequences. Third, while we demonstrate high biological fidelity, experimental validation is ultimately needed to confirm the activity of the sequences.

Future work will explore the use of pre-trained DNA foundation model backbones, such as Nucleotide Transformer v3 \cite{NTv3}, to enhance learned representations. We also plan to extend conditioning to diverse tissues and species, enabling an improved understanding of tissue-specific regulatory grammars and evolutionary constraints. Finally, using sequence-to-activity models, we intend to apply DNA-CRAFT to clinically relevant cell types and experimentally validate its designs.

\bibliography{iclr2026_conference}
\bibliographystyle{iclr2026_conference}

\appendix
\newpage
\section{Supplementary Material and Appendix}

The appendix consists of five sections. The first section (Appendix \ref{app:related work}) is an extension of the introduction, discussing work related to DNA-CRAFT. The second section (Appendix \ref{app:diffusion_training}) covers the training details of DNA-CRAFT's class-conditioned diffusion model. The third section (Appendix \ref{app:class_cond_details}) includes supplementary data for the classifier-free guidance related experiments. The fourth section (Appendix \ref{app:benchmark_details}) covers details of the regulatory sequence design tasks, and the last section (Appendix \ref{app:ablation_studies}) consists of ablation studies conducted for DNA-CRAFT. 


\subsection{Related work}
\label{app:related work}
% New related work section
Machine learning methods for regulatory element design rely on sequence-to-activity neural networks. These models are trained on large-scale genomic data to predict gene expression or chromatin accessibility from DNA sequences \cite{enformer,linder_predicting_2025}. By generalizing to unseen sequences, these models enable the design of regulatory elements with the desired activity. Existing approaches generally fall into two distinct categories: DNA sequence optimization methods and generative AI-based methods.

\paragraph{DNA Sequence Optimization Methods.}
Sequence optimization methods treat regulatory DNA design as a search problem. These approaches utilize a pre-trained sequence-to-activity model as a reward function to guide the search toward sequences with high activity. Classical greedy approaches, including simulated annealing \cite{laarhoven_simulated_1987}, \textit{in silico} mutagenesis, AdaLead \cite{sinai2020adalead}, and gradient-based algorithms \cite{schreiber_programmatic_2025}, start the process with random or known sequences and iteratively mutate them to maximize predicted activity. More recently, reinforcement learning (RL) techniques, such as DyNA-PPO \cite{angermueller_model-based_2019} and GFlowNets \cite{GFlowNet}, have been used to navigate this sequence search space more effectively. Because these methods focus on maximizing a single scalar reward, they may generate sequences that violate the regulatory grammar of natural DNA, and they are prone to converging on local optima \cite{vaishnav2022evolution}.

\paragraph{Generative AI for Regulatory Sequence Design.}
Generative AI approaches learn the underlying distribution of natural DNA sequences. Recent methods utilize autoregressive genomic language models (LMs) \cite{nguyen2023hyenadna,schiff_caduceus_2024,reglm}  and discrete diffusion models \cite{avdeyev2023dirichlet,sarkar2024designing,dasilva_designing_2026} to capture long-range sequence patterns with high fidelity. For example, the masked diffusion language model (MDLM) achieved strong performance on genomic benchmarks \cite{sahoo_simple_2024}. To use such generative priors for optimizing cell-type-specific regulatory activity, three alternative guidance mechanisms exist. \textbf{Classifier-free guidance} builds class-conditioned discrete diffusion models \cite{schiff_simple_2025}. In the context of regulatory sequence design, these models can be conditioned on sequences with high activity in desired cell types and then used to sample active sequences. \textbf{RL-based fine-tuning} updates the weights of the generative model to maximize a reward function \cite{uehara2024understandingreinforcementlearningbasedfinetuning}. Methods such as Ctrl-DNA use genomic LMs with constrained RL for cell-type-specific designs  \cite{chen_ctrl-dna_2025}. DRAKES backpropagates the reward gradients using the Gumbel-Softmax trick to fine-tune a discrete diffusion model for designing highly active enhancers \cite{wang_fine-tuning_2025}. While effective, fine-tuning is computationally expensive and requires updating the model parameters for every new design objective. \textbf{Inference-time alignment} methods steer the sampling process of a frozen diffusion model using external guidance, avoiding the cost of retraining \cite{uehara2025inferencetimealignmentdiffusionmodels}. Techniques like soft value-based decoding (SVDD) \cite{li_derivative-free_2024}, sequential monte carlo (SMC) \cite{phillips_particle_2024}, twisted diffusion sampling (TDS) \cite{wu_practical_2024}, and classifier guidance (CG) \cite{nisonoff_unlocking_2025} use reward-weighted resampling or auxiliary gradients computed by external sequence-to-activity models to steer the generative process. These methods typically optimize for high activity in one cell type, which often leads to high background activity in undesired cell types. Multi-objective inference-time alignment methods could address this and have been used successfully in other application areas, including peptide design \cite{tang_peptune_2024, chen2025multiobjectiveguideddiscreteflowmatching}.

\subsection{DNA-CRAFT Diffusion Model Training Details}
\label{app:diffusion_training}

\paragraph{Dataset Curation.} 
We trained DNA-CRAFT using the ENCODE Registry of candidate cis-Regulatory Elements V4 \cite{moore_expanded_2026}. To capture cross-species regulatory grammar and maximize biological diversity, we integrated data from both human (hg38) and mouse (mm10) genomes. The final dataset comprises 2,348,854 annotated regions across 1,888 human cell types and 926,843 annotated regions across 366 mouse cell types.

\paragraph{Data Pre-Processing.} 
DNA sequences corresponding to the regulatory regions were extracted from their respective reference genomes. All sequences were centered and padded to a fixed length of 350 base pairs (bp) using a distinct \texttt{[PAD]} token. To accommodate variable effective lengths, we implemented a masking mechanism within both the model backbone and the diffusion loss function, ensuring that padding tokens are excluded from the generative process. We applied reverse complement augmentation by taking either the forward or reverse complement strand with equal probability during training.

\paragraph{Class Consolidation.} 
The ENCODE V4 Registry categorizes regulatory elements based on biochemical signatures derived from DNase hypersensitivity, histone modifications, and CTCF binding. The original classification schema distinguishes between:
\begin{itemize}
    \item \textbf{Promoter-like (PLS):} Accessible regions proximal to transcription start sites (TSS) enriched for H3K4me3.
    \item \textbf{Enhancer-like (ELS):} Accessible regions enriched for H3K27ac, further stratified into proximal (pELS) and distal (dELS) based on TSS proximity.
    \item \textbf{CA-H3K4me3:} Accessible regions with H3K4me3 enrichment but low H3K27ac, often indicative of poised or primed regulatory states.
    \item \textbf{CA-CTCF:} Accessible regions enriched for CTCF binding sites with low histone acetylation, often indicating insulators.
    \item \textbf{CA-TF, CA, and TF:} Elements defined primarily by chromatin accessibility or transcription factor binding, lacking canonical histone marks.
\end{itemize}

We consolidated these fine-grained categories into five broad functional classes for DNA-CRAFT conditioning (Table \ref{tab:class_consolidation}).

\begin{table}[ht]
    \centering
    \caption{Mapping of ENCODE V4 cCRE classifications to DNA-CRAFT conditioning labels.}
    \label{tab:class_consolidation}
    \begin{tabular}{@{}ll@{}}
        \toprule
        \textbf{DNA-CRAFT Class} & \textbf{Original ENCODE Class} \\
        \midrule
        Promoter & PLS \\
        \addlinespace[0.4em]
        Enhancer & dELS, pELS \\
        \addlinespace[0.4em]
        CTCF & CA-CTCF \\
        \addlinespace[0.4em]
        Poised & CA-H3K4me3, TF \\
        \addlinespace[0.4em]
        Open Chromatin & CA, CA-TF \\
        \bottomrule
    \end{tabular}
    \vspace{-10pt}
\end{table}

\paragraph{Cross-Species Train-Test-Validation Split.} 
To ensure generalization and prevent overfitting due to sequence homology, we constructed our data splits using a graph-based clustering approach adapted from the Enformer training protocol \cite{enformer}. 

We constructed an undirected graph $G=(V, E)$ in which the vertices $V$ represent approximately 3.2 million processed regulatory elements. Edges $E$ were defined to capture both orthology and sequence similarity:
\begin{enumerate}[noitemsep, topsep=2pt, leftmargin=*]
    \item \textbf{Homology Edges:} An edge connects a human cCRE and a mouse cCRE if they share a sequence alignment of $>100$ bp, determined via the hg38-mm10 syntenic nets \cite{kent_human_2002}.
    \item \textbf{Overlap Edges:} Within a single species, an edge connects any two cCREs that share sequence similarity of more than $100$ bp.
\end{enumerate}

We computed the connected components of $G$ to define independent sequence clusters. These clusters were randomly partitioned into training (90\%), validation (5\%), and test (5\%) sets, ensuring a strict separation of homologous sequences across splits. 

\paragraph{Hyperparameters and Models.} 
We trained the model on the processed ENCODE dataset using the AdamW optimizer. To evaluate the impact of conditional generation, we trained two variants of DNA-CRAFT for 100 epochs each:
\begin{enumerate}
    \item \textbf{Unconditional Model:} Trained without classifier-free guidance (CFG) using a global batch size of 1,024.
    \item \textbf{Conditional Model:} Trained with CFG (dropout $p=0.1$) using a larger global batch size of 4,096 to ensure the representation of all 5 regulatory classes within every batch update.
\end{enumerate}

Model hyperparameters are provided in Table \ref{tab:hyperparams}.

\begin{table}[ht]
    \centering
    \caption{DNA-CRAFT Hyperparameters. The model utilizes a bidirectional DiMamba backbone.}
    \label{tab:hyperparams}
    \begin{tabular}{@{}ll@{}}
        \toprule
        \textbf{Hyperparameter} & \textbf{Value} \\
        \midrule
        \multicolumn{2}{l}{\textit{Backbone Architecture (DiMamba)}} \\
 Model Parameters&1.93 Million\\
        Sequence Length ($L$) & 350 \\
        Hidden Dimension ($d_{\text{model}}$) & 128 \\
        Mamba Blocks & 10 \\
        Bidirectional Strategy & Addition (Tied weights) \\
        Dropout & 0.1 \\
        \midrule
        \multicolumn{2}{l}{\textit{Diffusion Process}} \\
        Noise Schedule & Cosine \\
        Time Conditioning & True \\
        \midrule
        \multicolumn{2}{l}{\textit{Optimization}} \\
        Optimizer & AdamW \\
        Learning Rate & $1 \times 10^{-3}$ \\
        Training Epochs & 100 \\
        Batch Size & 1,024 (Uncond.) / 4,096 (Cond.) \\
        \midrule
        \multicolumn{2}{l}{\textit{Conditioning (CFG)}} \\
        Condition Type & Regulatory Element Class \\
        Number of Classes & 5 \\
        Condition Dropout & 0.1 \\
        Conditioning Dim & 128 \\
        \bottomrule
    \end{tabular}
\end{table}

\paragraph{Computational Infrastructure.} 
All experiments were conducted on NVIDIA H100 GPUs (80GB VRAM). The validation loss trajectories for both model variants are visualized in Figure \ref{fig:validation_curves}.

\begin{figure*}[ht] 
    \centering 
    \includegraphics[width=\linewidth]{figures/training_curves.png} 
    \caption{Validation loss curves for Unconditional and Conditional DNA-CRAFT models over 100 epochs.} 
    \label{fig:validation_curves} 
\end{figure*}

\subsection{Class-Conditioned Sampling and Motif Analysis}
\label{app:class_cond_details}

\paragraph{Latent Space Organization. }

To understand how class-specific sequence features are encoded within the model's representations, we analyzed the latent space of the generated sequences. We extracted latent representations from the final layer of the pre-trained DiMamba backbone for all test-set sequences. The embeddings were projected into two dimensions using t-Distributed Stochastic Neighbor Embedding (t-SNE) with a perplexity of 30 and a cosine distance metric. As shown in Figure \ref{fig:tsne_embeddings}, the model learns to separate sequences into clusters corresponding to their conditioning labels.
\begin{figure}[ht]
    \centering
    \includegraphics[width=0.7\linewidth]{figures/tsne_embeddings.png}
    \caption{Latent space organization of test set sequence embeddings. t-SNE visualization of the final-layer representations, colored by the conditioning regulatory label.}
    \label{fig:tsne_embeddings}
\end{figure}

\paragraph{Detailed Motif Enrichment Analysis.} 

To validate the biological relevance of the class-conditioned generated sequences, we performed a motif enrichment analysis. Figure \ref{fig:detailed_motif_heatmap} displays a heatmap of the Z-scores for the top 5 most specific motifs per class. The recovery of these specific factors aligns with known biological priors. Table \ref{tab:top_motifs_class} lists the top 5 enriched TFs for each class. To provide biological context, Table \ref{tab:tf_categories} maps these factors to their broad functional categories based on prior literature.

\begin{figure}[ht]
    \centering
    \includegraphics[width=0.7\linewidth]{figures/motif_enrichment_classified.png}
    \caption{Heatmap of Z-scores for the top 5 most enriched motifs (rows) and their corresponding regulatory sequence class (columns). }
    \label{fig:detailed_motif_heatmap}
    \vspace{-15pt}
\end{figure}

\begin{table}[ht]
    \centering
    \caption{Top 5 Enriched Transcription Factors per Regulatory Class. Factors are ranked by enrichment Z-score.}
    \label{tab:top_motifs_class}
    \begin{tabular}{@{}lp{0.6\textwidth}@{}}
        \toprule
        \textbf{Regulatory Class} & \textbf{Top Enriched Motifs} \\
        \midrule
        \textbf{CTCF} & CTCF, ZNF768, NFATC3, Zfp335, SNAI3 \\
        \addlinespace[0.3em]
        \textbf{Enhancer} & TFAP2C, MAFK, HES6, FOXJ2::ELF1, SPIC \\
        \addlinespace[0.3em]
        \textbf{Open Chromatin} & Nfat5, Foxo3, FOXO1::ELK3, FOSL2::JUND, FOXK1 \\
        \addlinespace[0.3em]
        \textbf{Poised} & LMX1A, TBX5, Prdm14, MEF2B, TBX2 \\
        \addlinespace[0.3em]
        \textbf{Promoter} & NKX6-2, FEV, NFYA, FLI1::DRGX, ELK1::SREBF2 \\
        \addlinespace[0.3em]
        \textbf{Unconditional} & MAFG::NFE2L1, FOS::JUN, Lhx3, FOSL1::JUNB, MAF::NFE2 \\
        \bottomrule
    \end{tabular}
\end{table}

\begin{table}[ht]
    \centering
    \caption{Biological Functional Categories of Enriched Transcription Factors. Classifications are derived from established biological literature \cite{motohashi_positive_2000, shi_identifying_2023, oshea_mechanism_1992, malik_role_2014, moon_fos-related_2017, villot_znf768_2021, decaesteker_tbx2_2018, pon_mef2_2015, seki_prdm14_2018, zhang_fosl2_2025, xu_hes6_2024, cao_transcription_2015, wang_fev_2013, chelban_mutations_2017, oldfield_nf-y_2019, hou_structure_2025, nilsson_elk1_2007, katsuoka_one_2000, lee_super-enhancer-guided_2019, laramee_opposing_2020, lunazzi_nfat5_2021, link_foxo_2025, sierra-pagan_foxk1_2023, yan_lmx1a_2011, smemo_regulatory_2012, ren_ctcf-mediated_2017, cockerill_nfat_2008, wang_zinc_2022, dahlem_overexpression_2012}.}
    \label{tab:tf_categories}
    \begin{tabular}{@{}lp{0.65\textwidth}@{}}
        \toprule
        \textbf{Biological Category} & \textbf{Transcription Factors} \\
        \midrule
        Chromatin Accessibility & Nfat5, Foxo3, FOXO1::ELK3, FOSL2::JUND, FOXK1 \\
        \addlinespace[0.4em]
        Developmental Regulators & Lhx3, NKX6-2, FEV, LMX1A, TBX5, Prdm14, MEF2B, TBX2, Zfp335 \\
        \addlinespace[0.4em]
        General Response Factors & MAFG::NFE2L1, FOS::JUN, FOSL1::JUNB, ZNF768 \\
        \addlinespace[0.4em]
        Insulators \& Architecture & CTCF \\
        \addlinespace[0.4em]
        Lineage Enhancers & MAF::NFE2, TFAP2C, MAFK, HES6, FOXJ2::ELF1, SPIC, NFATC3, SNAI3 \\
        \addlinespace[0.4em]
        Promoter Binding Factors & NFYA, FLI1::DRGX, ELK1::SREBF2 \\
        \bottomrule
    \end{tabular}
\end{table}

\subsection{Regulatory Sequence Design Benchmarks}
\label{app:benchmark_details}

\paragraph{Benchmarking Model Implementation Details.}

For all benchmark comparisons, we generated 128 sequences per experimental run. All experiments were repeated using independent random seeds to ensure statistical robustness. To ensure a fair comparison, all methods utilized the exact same \texttt{Design-Model} for optimization or guidance.

\begin{enumerate}
    \item \textbf{Ledidi:} We initialized the optimization with 128 random DNA sequences. We implemented a custom differentiable wrapper to compute MinGap scores from \texttt{Design-Model}'s output and backpropagate gradients directly to the input sequence representation. Optimization was conducted independently for each sequence for a maximum of 20,000 steps to ensure convergence.
    \item \textbf{Classifier Guidance (CG):} We used DNA-CRAFT's unconditional base diffusion model, trained on the entire ENCODE registry of regulatory elements without further fine-tuning for any experiments. We performed 128 parallel diffusion inference steps using our pre-trained unconditional diffusion model. Gradients were computed via the \texttt{Design-Model} wrapper to guide the sampling trajectory. We utilized a guidance scale of $\gamma=1000$.
    \item \textbf{Sequential Monte Carlo (SMC):} We used the same unconditional base diffusion model and MinGap wrapper as the CG method. The sampling process tracked 128 particles and applied a resampling parameter of $\alpha=0.5$.
    \item \textbf{Twisted Diffusion Sampling (TDS):} We followed the same setup as CG and SMC for this baseline. We applied a guidance scale of $\gamma=1000$ and a resampling parameter of $\alpha=0.5$.
    \item \textbf{D3 (Discrete Denoising Diffusion):} We trained the discrete diffusion model utilizing the transformer backbone (2M parameters) for a 100 epochs on the MPRA dataset (${\sim}$700,000 sequences) with the cell type activity as classes. We generated 128 sequences per cell type with conditional sampling ($\gamma=4.0$).
    \item \textbf{Ctrl-DNA:} We followed the original protocol and hyperparameters specified for each target cell type. We fine-tuned three separate models (one for each cell line: HepG2, K562, SK-N-SH) for 100 optimization steps. The top 128 sequences from each fine-tuning run were selected for evaluation. We note that Ctrl-DNA's base autoregressive model \cite{nguyen2023hyenadna} is trained on the entire human reference genome, which is a substantially larger and more diverse training corpus than the ENCODE registry of 3.2 million cCREs used to train DNA-CRAFT's diffusion backbone. Additionally, the TFBS regularization term was excluded, as the specific motif lists were not available in the public repository.
    \item \textbf{DRAKES:} We followed the protocol described in the original publication. For the HepG2 cell line, we utilized the provided pre-trained checkpoint. Similarly, we fine-tuned two separate models for K562 and SK-N-SH. We generated sequences using the respective fine-tuned models. We note that DRAKES fine-tunes its diffusion model using reward gradients computed over the full MPRA dataset (${\sim}$700,000 sequences), which encompasses the data used to train both our \texttt{Design-Model} and \texttt{Evaluation-Model}. This gives DRAKES implicit access to the evaluation distribution during its fine-tuning process.
    \item \textbf{DNA-CRAFT (Ours):} We employ DNA-CRAFT's class-conditioned base diffusion model, which is trained on the ENCODE dataset without further fine-tuning for all experiments. Candidate sequences were generated using conditional Monte Carlo tree guidance. We selected the final candidate from the MinGap set $\mathcal{G}^*$ at the end of the tree search. Table \ref{tab:dnacraft_params} details the specific inference configuration.
\end{enumerate}

\begin{table}[ht]
    \centering
    \caption{DNA-CRAFT Inference Parameters. Settings for the MCTS-guided diffusion sampling.}
    \label{tab:dnacraft_params}
    \begin{tabular}{@{}ll@{}}
        \toprule
        \textbf{Parameter} & \textbf{Value} \\
        \midrule
        \multicolumn{2}{l}{\textit{Diffusion Sampling}} \\
        Sampling Steps & 64 \\
        \midrule
        \multicolumn{2}{l}{\textit{Classifier-Free Guidance}} \\
        Guidance Scale ($\gamma$) & 3.0 \\
        Conditioning Class & Enhancer \\
        \midrule
        \multicolumn{2}{l}{\textit{Monte Carlo Tree Guidance}} \\
        Total Iterations & 64 \\
        Number of Children & 128 \\
        Exploration Coefficient & 0.5 \\
        $N_{\text{max}}$& 64 \\
        \bottomrule
    \end{tabular}
\end{table}

\paragraph{Extended Benchmark Results}
\label{app:extended_benchmarks}

We extended our evaluation to include cross-architecture and cross-study validation metrics. To validate the robustness and biological plausibility of our designs beyond the training distribution, we employed external models from \cite{lal_grelu_2025} to perform cross-model and cross-study evaluations:

\begin{itemize}
    \item \textbf{Complete Dataset Validation:} We evaluated the predicted activity of the generated sequences using a model trained on the full MPRA dataset \cite{gosai2024machine}, ensuring that the performance was not an artifact of the dataset split used during optimization.
    \item \textbf{Cross-Study Validation:} We utilized models trained on an independent MPRA study involving HepG2, K562, and induced pluripotent stem cells (WTC11) by \cite{agarwal_massively_2025}. We analyzed sequences designed for the shared HepG2 and K562 cell lines to verify their generalizability across different experiments. MinGap scores for the shared cell lines were calculated considering all three cell lines, despite not actively optimizing for WTC11 during the design process. Since this study did not include SK-N-SH cells, we excluded them from the analysis.
    \item \textbf{Cross-Modality Validation:} We predicted binary chromatin accessibility using an independent classifier and calculated the proportion of designed sequences with a predicted accessibility probability $>0.5$.
\end{itemize}

Table \ref{tab:enhancer_results_extended} presents the comprehensive performance across all metrics. In figure \ref{fig:tradeoff_benchmarks}, we visualize the trade-off between cell-type-specific activity and biological fidelity. 


\begin{table*}[!ht]
\centering
\caption{Comparison of methods to design enhancer specific across three human cell lines. Shown are various MinGap scores from three different studies, motif correlation, 3-mer correlation, fraction accessibility and diversity. Values are reported as mean (std) over 3 independent runs.}
\label{tab:enhancer_results_extended}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llccccccc}
\toprule
\textbf{Cell Line} & \textbf{Metric} & \textbf{SMC} & \textbf{CG} & \textbf{TDS} & \textbf{DRAKES} & \textbf{Ledidi} & \textbf{Ctrl-DNA} & \textbf{DNA-CRAFT} \\
\midrule
\multirow{7}{*}{\textbf{HepG2}}
& MinGap Eval $\uparrow$      & 1.614 (1.665) & -0.226 (0.096) & 0.404 (0.569) & -1.401 (0.054) & 5.771 (0.053) & \textbf{7.786 (0.070)} & 4.346 (0.050) \\
& MinGap (Full MPRA) $\uparrow$   & 1.472 (1.473) & -0.235 (0.074) & 0.482 (0.673) & -1.351 (0.036) & 6.484 (0.065) & \textbf{8.572 (0.186)} & 4.501 (0.053) \\
& MinGap (Agarwal) $\uparrow$ & 0.359 (0.571) & -0.189 (0.017) & -0.161 (0.103) & -0.847 (0.068) & 2.057 (0.043) & \textbf{3.232 (0.179)} & 1.500 (0.059) \\
& Motif Corr. $\uparrow$      & 0.554 (0.049) & 0.860 (0.009) & 0.397 (0.096) & 0.057 (0.013) & 0.584 (0.025) & 0.629 (0.045) & \textbf{0.921 (0.006)} \\
& 3-mer Corr. $\uparrow$      & 0.808 (0.102) & 0.968 (0.003) & 0.744 (0.098) & -0.361 (0.012) & 0.755 (0.013) & 0.494 (0.028) & \textbf{0.980 (0.009)} \\
& Fraction Acc. $\uparrow$    & 0.281 (0.474) & 0.016 (0.008) & 0.141 (0.141) & 0.940 (0.012) & 0.914 (0.021) & \textbf{1.000 (0.000)} & 0.966 (0.020) \\
& Diversity $\uparrow$        & 0.828 (0.432) & 1.976 (0.002) & 0.956 (0.096) & 1.864 (0.002) & \textbf{1.981 (0.001)} & 1.897 (0.026) & 1.979 (0.000) \\
\midrule
\multirow{7}{*}{\textbf{K562}}
& MinGap Eval $\uparrow$      & 4.124 (0.893) & -0.003 (0.046) & 1.622 (1.611) & -0.202 (0.067) & 7.662 (0.154) & \textbf{9.067 (0.170)} & 5.686 (0.043) \\
& MinGap (Full MPRA) $\uparrow$   & 4.166 (1.050) & -0.031 (0.041) & 1.523 (1.536) & -0.170 (0.048) & 8.395 (0.163) & \textbf{9.874 (0.212)} & 5.831 (0.059) \\
& MinGap (Agarwal) $\uparrow$ & 1.144 (0.551) & 0.140 (0.047) & 0.328 (0.334) & 0.187 (0.013) & 2.636 (0.027) & \textbf{3.020 (0.251)} & 1.648 (0.045) \\
& Motif Corr. $\uparrow$      & 0.454 (0.025) & 0.849 (0.026) & 0.511 (0.130) & 0.143 (0.024) & 0.647 (0.039) & 0.634 (0.084) & \textbf{0.933 (0.010)} \\
& 3-mer Corr. $\uparrow$      & 0.659 (0.133) & 0.940 (0.010) & 0.647 (0.198) & -0.354 (0.007) & 0.689 (0.022) & 0.413 (0.058) & \textbf{0.976 (0.000)} \\
& Fraction Acc. $\uparrow$    & 0.451 (0.393) & 0.021 (0.012) & 0.380 (0.541) & 0.526 (0.023) & 0.971 (0.012) & \textbf{1.000 (0.000)} & 0.930 (0.008) \\
& Diversity $\uparrow$        & 0.309 (0.112) & 1.977 (0.001) & 0.637 (0.523) & 1.958 (0.003) & 1.980 (0.001) & 1.896 (0.021) & \textbf{1.981 (0.001)} \\
\midrule
\multirow{7}{*}{\textbf{SK-N-SH}}& MinGap Eval $\uparrow$      & 0.556 (0.146) & -0.278 (0.006) & 0.186 (0.332) & 0.094 (0.046) & 3.026 (0.222) & \textbf{3.720 (0.179)} & 3.230 (0.022) \\
& MinGap (Full MPRA) $\uparrow$   & 0.647 (0.197) & -0.261 (0.013) & 0.167 (0.263) & 0.026 (0.067) & 3.587 (0.262) & 3.656 (0.265) & \textbf{3.698 (0.041)} \\
& MinGap (Agarwal) $\uparrow$ & -& -& -& -& -& -& -\\
& Motif Corr. $\uparrow$      & 0.519 (0.155) & 0.855 (0.026) & 0.476 (0.092) & 0.226 (0.017) & 0.380 (0.043) & 0.477 (0.037) & \textbf{0.881 (0.031)} \\
& 3-mer Corr. $\uparrow$      & 0.775 (0.035) & 0.949 (0.007) & 0.719 (0.030) & -0.382 (0.001) & 0.366 (0.019) & 0.201 (0.172) & \textbf{0.969 (0.007)} \\
& Fraction Acc. $\uparrow$    & 0.049 (0.066) & 0.016 (0.014) & 0.039 (0.034) & 0.820 (0.031) & \textbf{0.836 (0.039)} & 0.638 (0.424) & 0.747 (0.027) \\
& Diversity $\uparrow$        & 1.269 (0.108) & 1.976 (0.002) & 0.918 (0.211) & 1.826 (0.001) & \textbf{1.981 (0.002)} & 1.855 (0.091) & 1.976 (0.002) \\
\bottomrule
\end{tabular}%
}
\end{table*}

\begin{figure}[ht]
    \includegraphics[width=\linewidth]{figures/benchmark_tradeoffs.png}
    \caption{Trade-off between cell-type specificity and biological fidelity. 
    Performance of DNA-CRAFT compared to baselines for HepG2, K562, and SK-N-SH cell lines. The x-axis represents the MinGap score, serving as a proxy for cell-type-specific activity. The y-axis represents biological fidelity, measured by JASPAR Motif Correlation and 3-mer Correlation relative to top specific natural enhancers.}
    \label{fig:tradeoff_benchmarks}
    \vspace{-10pt}
\end{figure}


\textbf{Sequence-to-activity Model Training Details. }Both the \texttt{Design-Model} and \texttt{Evaluation-Model} were fine-tuned based on the Enformer architecture, adapted for output tasks corresponding to the target cell lines. Models were trained for 10 epochs using the Adam optimizer with a learning rate of $1 \times 10^{-4}$ and a global batch size of 512.

\subsection{Ablation Studies}
\label{app:ablation_studies}
\begin{table}[ht]
\centering
\caption{Ablation study on MinGap reward and class guidance. We compare variants of DNA-CRAFT with randomly generated and unguided sampled baselines. Results are generated for \textbf{SK-N-SH} cell-line-specific sequences. Values are reported as mean over sequences generated from a single run.}
\label{tab:abalation}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lccccccc}
\toprule
\textbf{Method} & \textbf{SK-N-SH} $\uparrow$ & \textbf{HepG2} $\downarrow$ & \textbf{K562} $\downarrow$ & \textbf{MinGap} $\uparrow$ & \textbf{Motif Corr.} $\uparrow$ & \textbf{3-mer Corr.} $\uparrow$ & \textbf{Diversity} $\uparrow$ \\

\midrule
\multicolumn{8}{l}{\textit{Baselines}} \\
Random & 0.770& 0.787& 0.893& -0.122& 0.325& 0.230& 1.981 \\
Unguided Sampling& 0.536& 0.656& 0.694& -0.158& 0.846& 0.916& \textbf{1.982}\\
\midrule
\multicolumn{8}{l}{\textit{MinGap Reward Ablation}} \\
DNA-CRAFT-Pareto & 1.058 & -0.063 & -0.256 & 1.121 & 0.854 & 0.911 & 1.980 \\
\midrule
\multicolumn{8}{l}{\textit{Class Guidance Ablation}} \\
DNA-CRAFT (Uncond., $  \gamma=0  $) & 4.885 & 1.685 & 1.095 & 3.200& 0.877& 0.965& 1.974 \\
DNA-CRAFT (Promoter, $  \gamma=3  $) & \textbf{6.452}& 4.047 & 3.993 & 2.405 & 0.447 & 0.092 & 1.920\\
DNA-CRAFT (Enhancer, $  \gamma=3  $) & 5.063& 1.723 & 1.065 & \textbf{3.340}& \textbf{0.906}& \textbf{0.975}& 1.977 \\
\bottomrule
\end{tabular}%
}
\vspace{-15pt}
\end{table}

\textbf{MinGap reward for Monte Carlo Tree Guidance.} MCTG with a MinGap reward seeks to balance high activity in desired cell types with low activity in undesired cell types. To validate this, we tested random and diffusion-sampled sequences without tree guidance as a baseline. We also tested MCTG as implemented in PepTune \cite{tang_peptune_2024} using Pareto front optimization, treating the desired cell type activity as a maximization objective and undesired activities as minimization objectives (DNA-CRAFT-Pareto). Table \ref{tab:abalation} shows that standard sampling fails to consistently generate sequences with high specificity, highlighting the need for tree guidance. Replacing the MinGap set with the Pareto front yielded unspecific sequences since Pareto optimization retains sequences that excel in any one of the objectives, irrespective of their performance in other objectives.

\textbf{Regulatory Sequence Class Guidance.} Among all classes of regulatory elements, enhancers exhibit the highest degree of cell-type specificity, functioning as the key drivers of cell-type-specific gene expression programs \cite{friedman_enhancerpromoter_2024}. Hence, we tested whether conditioning the generative process towards enhancer like sequences could achieve higher specificity. We generated sequences unconditionally ($\gamma=0$) and conditioned on the "Enhancer" or "Promoter" classes with $\gamma=3$, respectively. Table \ref{tab:abalation} shows that the "Enhancer" class conditioning indeed improved specificity, as well as motif correlation and diversity compared to unconditional and "Promoter"-conditional generation.


In summary, the ablation study suggests that using both the MinGap specificity score and class-conditioned sampling, as incorporated in DNA-CRAFT, improves the biological fidelity and predicted cell-type specificity of the designed sequences.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\end{document}
