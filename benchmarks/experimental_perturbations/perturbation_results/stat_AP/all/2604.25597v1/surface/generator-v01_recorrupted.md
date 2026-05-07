



\documentclass[a4paper, 10pt]{cas-sc}
\usepackage[numbers,sort]{natbib}
\def\tsc#1{\csdef{#1}{\textsc{\lowercase{#1}}\xspace}}
\tsc{WGM}
\tsc{QE}
\tsc{EP}
\tsc{PMS}
\tsc{BEC}
\tsc{DE}

\ExplSyntaxOn
\keys_set:nn { stm / mktitle } { nologo }
\ExplSyntaxOff

\usepackage{amsmath,amssymb,amsfonts}
\usepackage{booktabs}
\usepackage[table]{xcolor}
\usepackage{graphicx}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{hyperref}
\usepackage{url}
\usepackage{multirow}
\usepackage{enumitem}
\usepackage{subcaption}
\usepackage{siunitx}
\sisetup{
  table-number-alignment = center,
  detect-weight = true,
  detect-family = true
}

\begin{document}
\let\WriteBookmarks\relax

\shorttitle{Generating Synthetic Citation Networks with Communities}

\shortauthors{Brzozowski, Gagolewski, Siudem}

\title [mode = title]{Generating Synthetic Citation Networks with Communities}


\author[a]{{Ł}ukasz Brzozowski}[orcid=0000-0002-3625-3312]
\ead{lukasz.brzozowski@pw.edu.pl}
\cortext[cor1]{Corresponding author}
\cormark[1]
\credit{Conceptualisation of this study, Methodology, Investigation, Formal Analysis, Visualisation, Software, Writing}


\author[a,b]{Marek Gagolewski}[orcid=0000-0003-0637-6028]
\ead{marek.gagolewski@pw.edu.pl}
\ead[url]{https://www.gagolewski.com/}
\credit{Conceptualisation of this study, Methodology, Investigation, Writing, Supervision}


\author[c]{Grzegorz Siudem}[orcid=0000-0002-9391-6477]
\ead{grzegorz.siudem@pw.edu.pl}
\ead[URL]{https://siudem.fizyka.pw.edu.pl/}
\credit{Conceptualisation of this study, Methodology, Investigation, Formal Analysis, Writing}

\shortauthors{Brzozowski, Gagolewski, Siudem}

\address[a]{Warsaw~University of Technology, Faculty of Mathematics and Information Science, ul. Koszykowa 75, 00-662 Warsaw, Poland}

\address[b]{Systems Research Institute, Polish Academy of Sciences,
ul. Newelska 6, 01-447 Warsaw, Poland}

\address[c]{Warsaw~University of Technology, Faculty of Physics,
ul. Koszykowa 75, 00-662 Warsaw, Poland}


\begin{abstract}
Generating realistic synthetic citation, patent, or component dependency networks is essential for benchmarking community detection, graph visualisation, and network data mining algorithms. We present the first systematic comparison of generators of directed graphs that are nearly acyclic and have a ground-truth community structure. We evaluate 12 methods across 7 real citation networks and 26 metrics. We propose the practice of reversing directions of edges in static generators to break cycles and induce a citation-like flow, which significantly improves the performance of a degree-corrected Stochastic Block Model. Our novel methodological approach to evaluating community detection benchmarks distinguishes between endogenous and exogenous mesoscopic similarities, with the latter proving more important. This distinction reveals that high-parameter models suffer from overfitting by memorising planted community statistics which lead to their failing to produce realistic networks. Finally, we introduce the Citation Seeder (CS) algorithm, an iterative generator grounded in the Price-Pareto model of citation networks, with interpretable parameters and $O(N + E)$ runtime. CS achieves competitive results against the best-performing baselines while using up to four orders of magnitude fewer parameters and providing a clean framework for explaining and predicting a network's future growth.
\end{abstract}

\begin{keywords}
networks \sep graphs \sep community detection \sep clustering \sep stochastic block model \sep benchmarking
\end{keywords}

\maketitle


\section{Introduction}\label{sec:intro}

Citation and patent networks are amongst the most studied real-world networks. They are characterised by a structurally distinct topology: they are directed, nearly acyclic graphs (near-DAGs) that exhibit community structures representing scientific fields or patent classifiers. Despite their prevalence~\citep{speidel2015}, the synthetic generation of this specific graph family remains underserved. Existing community-aware generators produce undirected or densely cyclic graphs that lack the temporal citation flow structure (new papers cite older ones). This limits our ability to reliably benchmark community detection algorithms, test link-prediction models, and study network growth processes on controlled synthetic data.



More precisely, the scale-free nature of citation distributions has long been explained through the lens of cumulative advantage, whereby papers that have been cited many times are more likely to be cited again, resulting in a power-law-like tail~\citep{wang2013, newman2009}. Derek de Solla Price was among the first to formalise this mechanism in the context of scientific networks, proposing a growth model where new papers cite existing ones preferentially based on their in-degrees~\citep{deSollaPrice1965}. This concept, rooted in earlier ideas like Yule's and Simon's ``rich-get-richer'' processes, was later generalised by the Barabási–Albert model, which introduced continuous growth and linear preferential attachment to explain scale-free properties across networks~\citep{BA-model, newman2009}. However, pure preferential attachment exhibits a strong bias towards older nodes, preventing newer papers from gaining prominence. To address this, subsequent models incorporated intrinsic node \textit{fitness}—an inherent quality or attractiveness of papers that modulates attachment probability, as in the Bianconi–Barabási fitness model, enabling high-fitness latecomers to outperform incumbents  \citep{BB-model, vahan_nanumyan_c472afff}. Additionally, \textit{temporal attention decay} (or ageing) mechanisms were introduced, often modelled via exponential or log-normal functions that diminish a paper's citability over calendar time, better capturing the empirical rise-and-fall life cycle of scientific impact  \citep{Hu2021}.

While growth models capture temporal dynamics, a parallel stream of research has focused on generating networks with planted modular structures. The Stochastic Block Model (SBM)~\citep{lee-sbm} and its Degree-Corrected variant (DC-SBM)~\citep{karrer2011dcsbm} serve as generative baselines for networks with latent group assignments. Other widely used approaches include the Configuration Model~\citep{cm1980}, which preserves exact degree sequences without community awareness, and the LFR Benchmark~\citep{lancichinetti-lfr}, designed to produce power-law degree and community-size distributions. Recent approaches also include, e.g., adjusted modularity optimization~\citep{zhu2020} and deep generative models, such as Graph Variational Autoencoders~\citep{gvae} or autoregressive graph models~\citep{rtm-model}. Alternative approaches have attempted to combine community-aware detection with growth dynamics~\citep{nath2021}; while highly flexible, these methods often act as structural black boxes, lacking the analytical tractability and interpretability of pure random graph models limiting their uses to solely mechanistic tasks.

A notable gap exists between temporal citation-specific growth models and static community-aware graph generators. In a comprehensive survey of random graph modelling concepts, \cite{Drobyshevskiy-survey} analysed numerous generators exploiting principles like preferential attachment and stochastic block models, revealing fundamental limitations in integrating community structure with growth dynamics akin to citation networks; similarly, \cite{angela_bonifati_9f84e862} reviewed state-of-the-art graph generators (including SBM, LFR, and configuration models) and highlighted their inability to simultaneously capture realistic modularity, scale-free degrees, and directed acyclic topologies. Furthermore, classical community-aware models natively produce undirected graphs or densely cyclic directed graphs~\citep{metzler2019}, deviating from the inherently acyclic temporal flow of citation networks. Consequently, they cannot be directly applied or compared to real citation data without undergoing a structural transformation.

\medskip
Let us also note that the evaluation of community detection algorithms relies heavily on synthetic benchmarks with ground-truth labels. While the LFR benchmark is the \emph{de facto} standard for undirected networks, no widely adopted equivalent exists for directed, nearly acyclic graphs. The existing propositions rely on deep learning models that cannot scale to real data~\citep{alba_carballo_castro_fa8c0641}.

Theoretical limits of community detectability have been rigorously established for static undirected models, notably the phase transitions identified by~\cite{aur_lien_decelle_6fcd1196} for symmetric Stochastic Block Models, including the Kesten–Stigum (KS) threshold below which weak recovery (i.e., better-than-random guessing) becomes information-theoretically impossible \citep{cristopher_moore_cd59a506, emmanuel_abb__11402603}. These results distinguish scenarios where spectral methods or belief propagation succeed above the KS threshold, and while below it, no polynomial-time algorithm can detect communities reliably \cite{emmanuel_abb__8011b685}. However, these theoretical bounds primarily apply to undirected, symmetric SBMs without temporal ordering or directionality, and extensions to directed or asymmetric cases reveal additional challenges, such as shifted thresholds in sparse directed SBMs \citep{caltagirone2017, wilinski2019}.

Moreover, establishing such detectability limits is a fundamentally different task from providing generative benchmarks that mimic real-world structural complexity, especially for directed acyclic graphs like citation networks, where edges respect a temporal ordering and exhibit growth dynamics \citep{speidel2015}. A benchmark for citation networks must not only plant ground-truth labels but also replicate the specific topological flow -- preferential attachment within communities, ageing effects, and near-acyclic structure -- that algorithms rely on to partition the graph accurately~\citep{alba_carballo_castro_fa8c0641}. Static generators like LFR or degree-corrected SBMs produce undirected or cyclic directed graphs, failing to capture these traits without ad-hoc modifications \citep{angela_bonifati_9f84e862}. While edge deletions have been proposed to remove cycles in, e.g., taxonomy networks~\citep{Sun2017}, we are not aware of a systematic approach for cycle count reduction, not cycle deletion. Overall, adapting static generators to emulate citation-like flows is poorly understood. The practice of reversing the direction of edges to follow a heuristic topological ordering and re-introducing a fraction as back-edges has never been systematically evaluated for its effect on structural fidelity~\citep{karrernewman2009}.

\clearpage

\begin{figure}[bt!]
    \centering
    \includegraphics[width=0.5\linewidth]{figs/cdsi_cora.pdf}
    \caption{An example network generated by our algorithm with parameters estimated from the Cora citation network~\cite{cora-dataset}. The node colours correspond to the communities in the input network.}
    \label{fig:example}
\end{figure}


\medskip
To address the foregoing issues, in this paper, we make three primary contributions.

\begin{enumerate}
    \item \textbf{The CS generator.} We introduce the Citation Seeder (CS) algorithm, an iterative model grounded in the Price-Pareto model of citation networks \citep{brzozowski2025pricepareto}.
    This theoretical model distinguishes between accidental citations (allocated uniformly at random) and preferential citations (allocated proportionally to a vertex's in-degree, restricted to the node's community), yielding analytical, per-community Pareto type II in-degree distributions. However, the 3DSI and Price-Pareto frameworks inherently produce analytical degree sequences rather than complete graph topologies. They predict citation accumulation but do not specify the edge list, DAG structure, or clustering patterns, which is a limitation that necessitates the development of a generative counterpart.

    To generate $k$ communities, CS uses $2k$ analytically estimated parameters (where $k$ is the number of communities), operates in $O(N + E)$ generation time, and natively outputs a near-DAG. Across 26 structural metrics on 7 real citation networks, CS achieves a competitive mean rank against the best-performing baseline, the decycled Degree-Corrected Stochastic Block Model. CS achieves this result using up to four orders of magnitude fewer parameters and is not only parsimonious but \emph{explanatory}: its parameters are derived from a theory of network growth, with each parameter carrying a concrete bibliometric interpretation.

    \item \textbf{Systematic analysis of cycle breaking.} We formalise the cycle breaking procedure and evaluate its impact on five classical generators across six structural categories. We demonstrate that cycle breaking is not uniformly beneficial; for example, it dramatically improves the degree structure of the Degree-Corrected Stochastic Block Model \citep{karrer2011dcsbm} while simultaneously degrading its mesoscopic exogenous fidelity.

    \item \textbf{The endogenous/exogenous metric dichotomy.} We propose partitioning mesoscopic metrics into label-based (endogenous, such as modularity of ground truth partitions) and algorithm-behaviour-based (exogenous, such as modularity of algorithm-found partitions) categories. We argue that for the purpose of community-detection benchmarking, exogenous metrics are the primary concern. Decomposing the performance reveals that heavily parametrised models gain their rank almost entirely by memorising endogenous planted statistics. When evaluating true generative realism (exogenous metrics), the $O(k^2)$ CS model outperforms the $O(N-k^2)$ baseline.
\end{enumerate}


Overall, by introducing the CS generator, we aim to provide a unified framework for generating and researching citation-like networks. Unlike deep learning-based models that lack scalability and explainability~\citep{alba_carballo_castro_fa8c0641}, CS uses interpretable parameters to simulate field-specific growth rates, citation preferences, and inter-community interactions. Just like the methodological developments in the clustering of real-valued data \cite{clustering-benchmarks,cvi,VanMechelenETAL2023:whitepaperclustbench,UllmanETAL2022:wiresvalidationclust,JaegerBanks2023:clustanalrev, chen2022}, our tool allows researchers to evaluate community detection algorithms under specific, parametrised assumptions about how scientific fields grow, interact, merge, or split over time, facilitating studies of robustness to temporal biases and prediction of future network evolution~\citep{brisson2025}.







\section{The CS generator}\label{sec:cdsi}

In this section, we introduce the CS (Citation Seeder) algorithm, which is an iterative graph generator that produces directed near-DAGs with ground-truth community structure. It is inspired by the Price-Pareto model of citation networks with communities~\citep{brzozowski2025pricepareto}, extending that analytical framework from degree-sequence prediction to actual graph generation.
This section presents the theoretical foundation, the engineering modifications that bridge theory and practice, the generation algorithm, and the parameter estimation procedure.  A visualisation of an example network generated with the proposed algorithm is depicted in Figure~\ref{fig:example}.


\subsection{Theoretical foundation}\label{sec:theory}

Let us briefly summarise the Price-Pareto model with community structure \citep{brzozowski2025pricepareto}.
The model assumes that a citation network grows one node at a time under the following assumptions:
\begin{enumerate}[nosep,label=(\roman*)]
\item Each new node is assigned to community~$i$ with probability~$p_i>0$, where $\sum_{i=1}^{k} p_i > 1$.
\item The new node creates $m_i$ directed edges to existing nodes.
\item A fraction $(1 + \rho_i)m_i$ of these edges is distributed \emph{accidentally}: targets are chosen uniformly at random from the entire network, regardless of community.  The remaining fraction $\rho_j m_i$ is \emph{preferential}: targets are chosen with probability proportional to their current in-degree, restricted to the new node's own community.
\item Self-loops are disallowed.  Time is local to each community: the ``local time'' $t$ of community~$i$ equals its current size.
\end{enumerate}

Under these assumptions, \citep{brzozowski2025pricepareto} derives a closed-form expression for the expected in-degree of node~$\ell$ in community~$i$ at local time~$t$:
\begin{equation}\label{eq:indegree}
d_i^{(t)}(\ell) = \frac{\langle a \rangle}{\nu_i}\left[\frac{\Gamma(\ell - \nu_i)}{\Gamma(\ell)} \cdot \frac{\Gamma(t)}{\Gamma(t - \nu_i)} + 1\right],
\end{equation}
where the \emph{effective preferentiality} of community~$i$ and the global accidental citation rate
are defined, respectively, by:
\begin{equation}\label{eq:nu}
\nu_i = \frac{\rho_i m_i}{\langle a \rangle - \rho_i m_i}, \qquad \langle a \rangle = \sum_{j=1}^{k} p_j m_j (1 - \rho_j).
\end{equation}
The quantity $\nu_i \in (1,\infty)$ can be interpreted as the fraction of each local time step during which preferential citations accumulate; it reduces to $\rho$ in the single-community case
described in \citep{3dsi-pnas}.

Two theoretical results are central to CS's design.
First, as $t \to 0$, the in-degree distribution in community~$i$ converges to a \emph{Pareto type~II} (Lomax) distribution with shape $\alpha_i = \nu_i$ and scale $\lambda_i = \langle a \rangle \cdot \nu_i$.
Second, the preferentiality parameter $\rho_i$, which in general graphs is difficult to find, can be estimated under model's assumptions from the network using, i.a., Gini indices of in-degrees of all communities~\citep{lucio} (see Algorithm~\ref{alg:fit} for specific formulas). This connects in-degree inequality directly to the model parameters and is the basis for the parameter estimator Section~\ref{sec:estimation}, as well as for understanding and explaining the network topology and growth in terms of fitted parameters.

Unfortunately, this theoretical model produces a \emph{degree sequence}, not a graph.
It predicts how many citations each node will accumulate, but it does not specify the edge list, the DAG structure, nor the clustering patterns that emerge from the growth process.
CS bridges this gap: it implements the growth rules as an actual graph generator, adding the carefully engineered modifications described below to handle practical requirements that the analytical model abstracts away.


\subsection{From theory to the generator}\label{sec:engineering}

Each of the following adjustments is motivated by a specific gap between the theoretical model and real-world graph generation requirements.
All modifications preserve the invariant that the expectation of the out degree of a vertex is $m_i$
($\mathbb{E}[d_\mathrm{in}] = m_i$), ensuring that the theoretical predictions remain valid in expectation.


Algorithm~\ref{alg:cdsi} presents the complete DAG generation procedure.
Back-edge injection (Section~\ref{sec:backedge}) is applied as a post-processing step on the output of Algorithm~\ref{alg:cdsi} and is not shown to avoid clutter.

\begin{algorithm}[t!]
\caption{CS DAG Generation}\label{alg:cdsi}
\begin{algorithmic}[1]
\Require $N$, $k$, $\{p_i, m_i, \rho_i, \sigma^2_i\}_{i=1}^{N}$
\Ensure Directed graph $G = (V, E)$ with community labels
\State Create $k$ seed nodes (one per community); $\mathrm{Urn}_i \gets \emptyset$ for all~$i$
\For{$v = k+1$ \textbf{to} $N$}
    \State $c \gets \mathrm{Categorical}(p_1, \ldots, p_k)$; \quad $\mathrm{label}[v] \gets c$
    \If{$\sigma^2_c > m_c$} \Comment{Overdispersed out-degree}
        \State $r \gets m_c^2 / (\sigma^2_c - m_c)$;
        \State $p_\mathrm{nb} \gets m_c / \sigma^2_c$
        \State $\lambda \sim \mathrm{Gamma}(r, (1 - p_\mathrm{nb})/p_\mathrm{nb})$;
        \State $d_\mathrm{out} \gets \min(\mathrm{Poisson}(\lambda), v{-}1)$
    \Else
        \State $d_\mathrm{out} \gets \min(\mathrm{Poisson}(m_c), v{-}1)$
    \EndIf
    \State $n_\mathrm{acc} \sim \mathrm{Binomial}(d_\mathrm{out}, 1 - \rho_c)$;
    \State $n_\mathrm{pref} \gets d_\mathrm{out} - n_\mathrm{acc}$
    \State $T \gets \emptyset$
    \For{$j = 1$ \textbf{to} $n_\mathrm{acc}$} \Comment{Accidental targets}
        \State $T \gets T \cup \{\mathrm{Uniform}(0, \ldots, v{-}2)\}$
    \EndFor
    \For{$j = 1$ \textbf{to} $n_\mathrm{pref}$} \Comment{Preferential targets}
        \If{$|\mathrm{Urn}_c| > 0$}
            \State $u \sim \mathrm{Uniform}(0, \ldots, |\mathrm{Urn}_c|{-}1)$
            \State $T \gets T \cup \{\mathrm{Urn}_c[u]\}$
        \Else
            \State $u \sim \text{Uniform[community } c \setminus \{v\}]$
            \State $T \gets T \cup \{u\}$
        \EndIf
    \EndFor
    \For{each $u \in T$}
        \State $E \gets E \cup \{(v, u)\}$;
        \State $\mathrm{Urn}_{\mathrm{label}[u]} \gets \mathrm{Urn}_{\mathrm{label}[u]} \cup \{u\}$
    \EndFor
\EndFor
\end{algorithmic}
\end{algorithm}


\subsubsection{Stochastic out-degree with overdispersion}\label{sec:overdispersion}

The theoretical model assumes every node in community~$i$ creates exactly $m_i$ edges.
Real citation networks show substantial within-community variance in reference list lengths: some papers cite 3 references, others cite 80, even within the same field.
We introduce a fourth per-community parameter~$\sigma^2_i$ controlling out-degree variance.

If $\sigma^2_i > m_i$ (the overdispersed case, typical in practice), we draw the out-degree via a Gamma-Poisson compound:
\begin{align}
r &= m_i^2 / (\sigma^2_i + m_i), \quad p_\mathrm{nb} = m_i / \sigma^2_i, \nonumber \\
\lambda &\sim \mathrm{Gamma}\bigl(r,\; (1 - p_\mathrm{nb})/p_\mathrm{nb}\bigr), \nonumber \\
d_\mathrm{out} &= \min\bigl(\mathrm{Poisson}(\lambda),\; v - 1\bigr). \label{eq:outdegree}
\end{align}
This is equivalent to a Negative Binomial distribution with real-valued shape parameter~$r$ (the Gamma-Poisson compound avoids the integer truncation imposed by standard library implementations), giving $\mathbb{E}[d_\mathrm{out}] = m_i$ and $\mathrm{Var}[d_\mathrm{out}] = \sigma^2_i$.
If $\sigma^2_i \leq m_i$ (equi- or underdispersed), we fall back to $d_\mathrm{out} \sim \mathrm{Poisson}(m_i)$, giving $\mathbb{E}[d_\mathrm{out}] = \mathrm{Var}[d_\mathrm{out}] = m_i$.


\subsubsection{Stochastic accidental/preferential split}

The theoretical model deterministically allocates $(1 - \rho_i) m_i$ accidental and $\rho_i m_i$ preferential edges.
Since our $d_\mathrm{out}$ is now stochastic, the split must also be stochastic. Given the realised $d_\mathrm{out} = m$, we draw $n_\mathrm{acc} \sim \mathrm{Binomial}(m, 1 - \rho_i)$ and set $n_\mathrm{pref} = m - n_\mathrm{acc}$.
This preserves $\mathbb{E}[n_\mathrm{acc} / d_\mathrm{out}] = 1 - \rho_i$ in expectation.


\subsubsection{Urn-based preferential sampling}

Na\"ive preferential sampling -- computing all in-degrees, normalising, and drawing from the resulting distribution -- costs $O(N_i)$ per edge, giving $O(N E)$ total generation time, where $N_i$ is the number of vertices in community $i$.
We instead maintain a P\'olya urn per community: whenever node~$u$ receives an incoming edge, an additional copy of~$u$ is appended to its community's urn.
Drawing a preferential target reduces to sampling a uniform random element from the urn, which is $O(1)$.
The urn's composition is proportional to in-degree by construction.
Total cost of the DAG generation phase is $O(N + E)$.


\subsubsection{Cold-start handling}

At the beginning of generation, some communities have no edges yet, so their urns are empty.
Preferential sampling from an empty urn is undefined.
When this occurs, we fall back to uniform sampling from the community's existing members (excluding the new node to prevent self-loops).
This is equivalent to assuming all members are equally attractive before any citations exist, which is a reasonable initialisation that converges quickly to the true preferential distribution as the urn fills. Practically, the fall-back will happen at most  a few times ($\approx 1/m_i$) in each community.

The first $k$ nodes (one per community) are created as seed nodes without outgoing edges.


\subsubsection{Back-edge injection}\label{sec:backedge}

The growth model produces a strict DAG: every edge points from a newer node to an older one.
Real citation networks have a small fraction~$r$ of back-edges: papers citing future work added during revision, patents referencing later filings, simultaneous publications with cross-references.

After DAG generation, we inject back-edges to match the input graph's back-edge ratio~$r$.
The number of injected edges is $n_\mathrm{back} = \lfloor r \cdot |E| / (1 - r) \rfloor$, ensuring that the resulting fraction of back-edges equals~$r$.

When real timestamps are available (which is the case of the
DBLP and OGBN-ArXiv datasets described in Section~\ref{sec:datasets}), the back-edge set is identified directly from the temporal ordering.
Otherwise, we estimate~$r$ using a greedy heuristic: score each node by out-degree minus in-degree, sort in descending order, and declare any edge violating this ordering as a back-edge.
This runs in $O(N \log N + E)$ time.

CS's back-edge placement exploits the temporal ordering and community structure of the growth process:
\begin{itemize}[nosep]
\item Each candidate back-edge $(u \to v)$ requires $u < v$ in CS's node-ID ordering (older node cites newer).
\item Source-target pairs prefer small rank gaps (sampled via a geometric distribution with success probability $ 1 - \exp(-0.1)\approx 0.095$) and intra-community pairs (with a fixed intra-community probability of $0.8$).
\item Candidates are filtered against existing edges and previously accepted back-edges.
\item Collisions are rejected and resampled using an O(1) average-case hash-set lookup, eliminating the need for sorting or binary searches.
\end{itemize}

The back-edge injection phase operates in expected $O(N+E)$ time. This efficiency is achieved by using a hash-based set for duplicate detection (which takes $O(E)$ to build and provides $O(1)$ lookups) and an $O(N)$ single-pass community index for intra-community pair sampling. Combined with the $O(N+E)$ DAG generation phase, the total expected time complexity of CS is strictly $O(N+E)$.




\subsection{Parameter estimation}\label{sec:estimation}

All $4k$ parameters are estimated in closed form from the input graph's adjacency matrix and community labels (Algorithm~\ref{alg:fit}).
No iterative optimisation, gradient descent, or cross-validation is required.


The four parameters per community have concrete interpretations:
\begin{itemize}[nosep]
\item $p_i$: community growth probability -- the field's share of new publications.  Estimator: $N_i / N$ (direct count).
\item $m_i$: expected out-degree -- the typical reference list length in field~$i$.  Estimator: total out-degrees in community~$i$ divided by community size minus one.
\item $\sigma^2_i$: out-degree variance -- heterogeneity of referencing habits within the field.  Estimator: sample variance of out-degrees.
\item $\rho_i$: preferentiality -- the fraction of citations that are merit-driven (proportional to existing in-degree) rather than accidental.  Estimator: derived from the Gini coefficient of in-degrees via  \citep[Eq.~(19)]{brzozowski2025pricepareto};
see Step 9 of Algorithm~\ref{alg:fit}.
\end{itemize}

The estimation procedure runs in $O(N \log N)$ time, dominated by the sorting of in-degrees for the Gini computation.
Estimated $\hat{\rho}_i$ is clamped to $[\epsilon, 1 - \epsilon]$ with $\epsilon = 10^{-3}$ to ensure valid probabilities; clamping indicates the community may violate model assumptions.

When no input graph is available, all $4k$ parameters can be specified directly.
Every parameter has a concrete bibliometric interpretation, making it possible to construct synthetic networks from domain knowledge alone, for example, to generate a hypothetical citation network for a new field with specified growth rate, typical reference list length, and citation inequality.





\begin{algorithm}[t!]
\caption{CS Parameter Estimation}\label{alg:fit}
\begin{algorithmic}[1]
\Require Directed graph $G = (V, E)$, community labels $\ell : V \to \{1, \ldots, k\}$
\Ensure Parameters $\{p_i, m_i, \rho_i, \sigma^2_i\}_{i=1}^{k}$
\For{$i = 1$ \textbf{to} $k$}
    \State $N_i \gets |\{v : \ell(v) = i\}|$ \Comment{Community size}
    \State $\hat{p}_i \gets N_i / N$
    \State $\Psi_i \gets \sum_{v:\ell(v)=i} d_\mathrm{out}(v)$
    \State $\Sigma_i \gets \sum_{v:\ell(v)=i} d_\mathrm{in}(v)$
    \State $\hat{m}_i \gets \Psi_i / (N_i - 1)$ \Comment{Expected out-degree}
    \State $\hat{\sigma}^2_i \gets \frac{1}{N_i - 1}\bigl(\sum_{v:\ell(v)=i} (d_\mathrm{out}(v))^2 - N_i \hat{m}_i^2\bigr)$ \Comment{Out-degree variance}
    \State $G_i \gets \mathrm{Gini}\bigl(\{d_\mathrm{in}(v) : \ell(v) = i\}\bigr)$ \Comment{In-degree Gini}
    \State $\hat{\rho}_i \gets \dfrac{\Sigma_i\,(2G_i + N_i - 2 G_i N_i)}{\Psi_i\,(G_i + 1 - G_i N_i)}$ \Comment{Formula (19) in \citep{brzozowski2025pricepareto}}
\EndFor
\end{algorithmic}
\end{algorithm}




\begin{figure}[tb!]
\centering
\includegraphics[width=0.8\textwidth]{figs/fig_theory_validation.pdf}
\caption{\label{fig:theory_validation} CS-generated vs~theoretical in-degree distributions (Eq.~\ref{eq:indegree}), $N = 30{,}000$, $k = 3$, and $\rho = 0.2$ (low preferentiality, left),
$\rho = 0.5$ (moderate, centre) or $\rho = 0.9$ (high, right).
The theoretical CCDF is computed from the same parameters. Deviations in the tails reflect finite-size effects that diminish with increasing~$N$.}
\end{figure}





\subsection{Theory validation}\label{sec:validation}

Figure~\ref{fig:theory_validation} confirms that CS's generated in-degree distributions match the theoretical predictions of Equation~\ref{eq:indegree} across three parametrisations spanning the full range of preferentiality.


At $\rho = 0.2$ (low preferentiality, where most citations are accidental), the generated complementary CDF closely tracks the Pareto type~II prediction across the entire degree range.
At $\rho = 0.5$ (moderate preferentiality), theory and generation remain aligned over three orders of magnitude in degree.
At $\rho = 0.9$ (high preferentiality), the bulk of the distribution matches well, with visible deviation only in the extreme tail.
This is expected: at high~$\rho$, a small number of hub nodes accumulate disproportionate in-degree, and finite-size effects ($N = 30{,}000$) cause the empirical tail to fluctuate around the asymptotic prediction.
These deviations diminish with increasing~$N$, which is consistent with the theoretical convergence to Pareto type~II.

This validation is important because the theoretical CCDF is \emph{not fitted} to the generated data: both the curve and the generator use the same parameter values.
Agreement confirms that the engineered modifications described in Section~\ref{sec:engineering} (stochastic out-degree, urn-based sampling, cold-start handling) do not distort the theoretical degree structure in expectation.
The  evaluation on 26 metrics in Section~\ref{sec:results} will show that this theoretical fidelity extends well beyond the in-degrees: to structural properties the model was never designed to predict.




\section{Cycle breaking in other models}\label{sec:neardag}
In this section we define and motivate the process we call ``cycle breaking'', i.e., an adaptation of existing graph generators to the structure of citation-like networks that are sparse in cycles. Previously known static generators do not operate under the assumption of this sparsity. Instead, they copy and recreate estimated parameters and patterns without global constraints. As such, we first consider the process and explain choices made.


\subsection{The process}
The particular process we propose for adapting a graph generator's output into a citation-like network structure is simple, we describe it in points below.
\begin{itemize}
    \item Read input graph's timestamps to determine the chronological order of node appearance; if the timestamps are unavailable, use a greedy heuristic sorting nodes by $d_\text{out} - d_\text{in}$ to determine approximate order. Using the order found, compute the fraction of back-edges (i.e., going from older nodes to newer nodes) as $r$.
    \item Using the similar greedy heuristic process, assign a topological ordering to generator's output nodes. Then, reverse all edges to point from older nodes to newer nodes, creating a DAG.
    \item Select a fraction of $r$ edges from the newly created DAG at random and reverse them to create back-edges.
\end{itemize}


\subsection{Considered alternatives}
The above process, while intuitive and simple, should be meticulously scrutinised to make sure our proposition of cycle breaking is preferably unbiased and offers a fair ground for comparison of different generators:

\paragraph{Decycling first.} It would be plausible to skip the decycling step and try to obtain the ratio of $r$ back-edges directly from the generator's output. While it is possible, it necessarily poses a question ``which edges to reverse'' since the topological order, at this point, cannot be easily deduced; we believe any strategy selected would be biased toward the specific generator, and we hoped to achieve a model-agnostic procedure that can be compared between various generators. As such, we believe that beginning with the decycling is a reliable solution for creating a methodologically correct starting point to achieve truthful comparison.

\paragraph{Reversing vs~addition.} An alternative to the proposed approach would be adding back-edges instead of reversing existing edges. One could argue that by reversing the direction of existing edges we interrupt the flow patterns induced by each generator. To this we say that we have already interrupted this flow by enforcing the DAG structure, which is a necessary sacrifice for further consistency. We also argue that if, at this point, we added edges instead of reversing them, we introduce unnecessary bias caused by the variability of $r$ in different input graphs. By reversing edges, we exactly preserve the skeletal structure, sacrificing only the flow patterns of the graph.

\paragraph{Generator input.} There is another possibility: first remove back-edges from the input graph, fit the generator to produce the output, and then reintroduce a fraction of $r$ edges as back-edges. The difference between this approach and the above one is that the generated graphs are fitted to the DAG subgraph of input instead of noisy full version. We have considered this approach, but we believe it introduces a similar bias as described before: a fraction of $r$ edges in the output graph is not only reversed, but placed, against generator's output. This would, in our opinion, be a \textit{de facto} new hybrid model instead of a neutral modification of the baseline. Also, neither of the considered reference algorithms was designed with imitating a DAG network in mind, so we see no methodological benefit of fitting the model to the input graph stripped of back-edges.

With the exhaustive explanation of key choices above, we hope to offer a fair ground for comparison of effects of cycle breaking on reference algorithms.



\section{Experimental setup}\label{sec:setup}

This section describes the evaluation infrastructure shared by all analyses in the paper: the datasets, the generators under comparison, the structural metrics, and the statistical methodology.


\subsection{Datasets}\label{sec:datasets}

We evaluate all methods on seven directed networks with ground-truth community labels (Table~\ref{tab:datasets}).
These span three orders of magnitude in node count (from Cora with 2.7k~nodes to DBLP with 3.6M) and community counts ranging from 3 (PubMed) to 63k (DBLP), providing diversity in both scale and structural complexity. To the best of our knowledge, these seven networks represent the most comprehensive publicly available collection, because the available real-world networks satisfying all required conditions are simply very rare.

Here are some brief notes on individual datasets.
\textbf{Cit-Patents}~\citep{snapnets} is the only patent network in our benchmark suite; it is a patent citation graph with USPTO patent classifiers as communities.
\textbf{DBLP}~\citep{dblp-dataset} is the largest by node/edge count and community count; it is a paper-to-paper citation graph derived from the AMiner v14 database, with field-of-study metadata as community labels (field of science with highest weight was selected as the community label of each node).
\textbf{OGBN-ArXiv}~\citep{ogbn-arxiv} is a medium-scale paper citation graph (169K~nodes) with ArXiv category labels, widely used as a machine learning benchmark.
\textbf{Cora}, \textbf{CiteSeer}, and \textbf{PubMed} are smaller paper-to-paper standard benchmarks with field-of-study labels~\citep{cora-dataset}. \textbf{Cora-Full}~\citep{bojchevsky} is a lesser-known more comprehensive variant of the former of the three.
All datasets were downloaded and processed using the UnPACD repository~\citep{unpacd}. Cit-Patents and DBLP datasets contained significant fractions of nodes with missing community labels. For the purpose of our analysis, they were removed from the graphs.

\clearpage

\begin{table}[t!]
\centering
\caption{Datasets used in the evaluation. Datasets marked with an asterisk (*) were subsampled for the purpose of computing computationally expensive metrics (see~\ref{par:large_graph}). Value $N$ corresponds to numbers of nodes after pruning vertices without community labels, where it was required.}
\label{tab:datasets}
\small
\begin{tabular}{l
                S[table-format=7.0, group-separator={,}, group-minimum-digits=4]
                S[table-format=1.2]
                S[table-format=5.0, group-separator={,}, group-minimum-digits=4]
                l}
\toprule
Dataset & $N$ & $\hat{d}_\text{out}$ & $k$ & Timestamps\\
\midrule
    Cit-Patents*~\citep{snapnets} & 2755865 & 5.07 & 418 & Discarded \\
    CiteSeer~\citep{cora-dataset} & 3312 & 1.39 & 6 & Absent \\
    Cora~\citep{cora-dataset} & 2708 & 2.00 & 7 & Absent \\
    Cora-Full~\cite{bojchevsky} & 19793 & 3.30 & 70 & Absent \\
    DBLP*~\citep{dblp-dataset} &  3586177 & 6.24 & 62904 & Used \\
    OGBN-Arxiv*~\citep{ogbn-arxiv} & 169343 & 6.89 & 40 & Used \\
    PubMed~\citep{cora-dataset} & 19717 & 2.25 & 3 & Absent \\
\bottomrule
\end{tabular}
\end{table}


\begin{table}[t!]
\centering
\caption{Generator comparison. Note that for networks such as DBLP, the $k^2$ term heavily dominates.}
\label{tab:models}
\small
\begin{tabular}{lcc}
\toprule
Model & No. of parameters & Community support \\
\midrule
    ER & $O(1)$ & No \\
    Config\ Model & $O(N)$ & No \\
    LFR & $O(1)$ & Yes  \\
    SBM & $O(k^2)$ & Yes\\
    DC-SBM & $O(N{+}k^2)$ & Yes  \\
    \textbf{CS} & $O(k)$ & Yes  \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Generators under comparison}\label{sec:generators}


We compare 12~methods organised into three groups: baseline generators, community-aware generators, and CS variants. Every literature algorithm was considered in two versions: standard and adjusted with cycle breaking; see Table~\ref{tab:models} for summary.

\paragraph{Five classical generators (standard variants).}
We include Erd\H{o}s-R\'enyi (ER)~\citep{newman-networks}, the Configuration Model~\citep{newman-networks}, the Stochastic Block Model (SBM)~\citep{holland-sbm}, the Degree-Corrected SBM (DC-SBM)~\citep{karrer2011dcsbm}, and the LFR benchmark~\citep{lancichinetti-lfr}.
Each is fitted to an input graph's relevant statistics: edge density for ER, degree sequence for the Configuration Model, block connection matrix and community assignments for SBM and DC-SBM, and power-law exponents with mixing parameter for LFR.
These generators produce undirected or densely cyclic directed graphs; none natively outputs a DAG or near-DAG.

\paragraph{Five classical generators (near-DAG variants).}
Each standard generator is also evaluated after applying cycle breaking described in Section~\ref{sec:neardag}.
The transformation imposes a heuristic topological ordering on the generated graph, reverses the direction of edges to follow this ordering (producing a DAG), then reintroduces a fraction~$r$ of edges as uniformly random back-edges, where $r$ is the ratio of back-edges.
The resulting variants are denoted with a ``-nD'' suffix (e.g., DC-SBM-nD).
This doubling of the baseline count is deliberate: it allows us to evaluate cycle breaking's impact as a methodological question in its own right (Section~\ref{sec:neardag}), independent of the CS comparison.

\paragraph{CS and CS\,(DAG).}
The iterative generator CS was described in Section~\ref{sec:cdsi}.
It produces a directed near-DAG with planted community labels using $4k$~analytically estimated parameters ($k$ = number of communities): growth probability~$p_i$, expected out-degree~$m_i$, preferentiality~$\rho_i$, and out-degree variance~$\sigma^2_i$ for each community $i$. The CS\,(DAG) variant omits the back-edge injection step, producing a strict DAG.



\subsection{Structural metrics}\label{sec:metrics}

We evaluate structural fidelity by comparing each synthetic graph against the corresponding real graph across a battery of metrics.
Three distance measures are used, chosen to match the nature of each metric.
In all cases, lower values indicate better fidelity; zero indicates a perfect match:
\begin{itemize}[nosep]
\item \textbf{Absolute Percentage Error (APE)} for scalar graph properties (e.g., average path length, global clustering coefficient, modularity):
$\mathrm{APE} = |x_\mathrm{synth} - x_\mathrm{real}| / |x_\mathrm{real}|$.
\item \textbf{Wasserstein 1-distance ($W$)} for distributional properties (e.g., in-degree distribution, betweenness distribution, community-size distribution):
the minimum transport cost to transform one distribution into the other.
\item \textbf{$L_1$ distance} for the triad census (16~triad types), which has no canonical real-line ordering suitable for the Wasserstein distance:
$L_1 = \sum_t |p_\mathrm{synth}(t) - p_\mathrm{real}(t)|$.
\end{itemize}


\medskip
The 26~metrics\footnote{We started with 27~candidate metrics, and checked possible redundancy with the pairwise Spearman rank correlation $r_s$: for each pair of metrics with $|r_s| \geq 0.85$ (computed on within-cell standardised values, pooled across all datasets and methods), we retained only one. This procedure removed only a single metric (APE of ground-truth assortativity, redundant with other community-level metrics), yielding 26~retained metrics.} are organised into six structural categories, each capturing a distinct aspect of graph structure. Each metric belongs to exactly one category:

\begin{enumerate}[nosep]
\item \textbf{Global Topology} (3~metrics): APE of effective diameter, APE of average path length, $W$ of reachability distribution.
Captures large-scale connectivity and distance structure.

\item \textbf{Degree Structure} (4~metrics): $W$ of in-degree distribution, $W$ of out-degree distribution, APE of in-degree assortativity, APE of out-degree assortativity.
Captures degree distributions and degree-degree correlations.

\item \textbf{Mesoscopic Endogenous (Structure)} (6~metrics): APE of ground-truth modularity, APE of ground-truth conductance, APE of ground-truth inter-cluster edge density, APE of ground-truth intra-cluster edge density, $W$ of ground-truth in-degree participation, $W$ of ground-truth out-degree participation.
Captures how well the synthetic graph reproduces the statistical properties of the community structure the graph is assigned with by real labels; see Section~\ref{sec:endo_exo} for discussion.

\item \textbf{Mesoscopic Exogenous (Structure)} (6~metrics): APE of Infomap codelength, APE of Leiden modularity (with standard modularity quality function), APE of Leiden modularity (with RBConfiguration quality function), $W$ of Infomap community-size distribution, $W$ of Leiden community-size distribution (modularity), $W$ of Leiden community-size distribution (RBConfiguration).
Captures how community-detection algorithms \emph{behave} on the synthetic graph compared to the real input one; see Section~\ref{sec:endo_exo} for discussion.

\item \textbf{Local Structure} (4~metrics): APE of global clustering coefficient, APE of feed-forward loop count, $W$ of local clustering coefficient distribution, $L_1$ of triad census.
Captures clustering patterns, motifs, and triadic structure.

\item \textbf{Flow \& Connectivity} (3~metrics): $W$ of betweenness centrality distribution, $W$ of strongly connected component size distribution, $W$ of longest-path-length distribution.
Captures directed flow, component structure, and DAG depth. Back-edges were omitted when computing longest paths due to achieve tractable computation time.
\end{enumerate}


\subsection{The endogenous/exogenous distinction}\label{sec:endo_exo}

The partition of mesoscopic metrics into endogenous and exogenous categories requires some more detailed justification. We use the word ``endogenous'' as relating to the ground-truth partition vector supplied with each graph whilst ``exogenous'' indicates a partition found by an external classifier such as a community detection algorithm; similar usage can be found in~\cite{Legramanti2022exogenous}.

\paragraph{Endogenous mesoscopic metrics} compare the ground-truth community structure of the synthetic graph against that of the real graph, answering whether \emph{the planted communities in the synthetic graph share the statistical properties of the real ones}. These metrics take both the graph and its community labels as input.
While widely accepted as measures of concordance between input and generated graphs, we argue they are inherently biased by the interaction between \emph{externally imposed} topology (from ground-truth labels) and the graph's \emph{intrinsic} topology (natural density fluctuations). Consider two extremes. In some citation networks, these two align cleanly: intra-community connections dominate inter-community ones, making the graph a prime candidate for SBM fitting. In others, a community label is merely \emph{indicative} of a node's local connections rather than determinative -- it may describe a paper's citation tendencies without defining its full local structure. Such networks call for modelling tools better suited than a plain SBM.
More fundamentally, evaluating a generator on these metrics rewards similarity in the \emph{relationship} between topology and community labels across input and output, rather than similarity between the graphs themselves. We do not claim this is worthless -- but for downstream tasks such as community detection, it can mislead us into ``believing'' the generator faithfully imitates the input's structure when it has only matched a derived property.

\paragraph{Exogenous mesoscopic metrics} run the standalone community-detection algorithms (Infomap~\citep{Rosvall2009}, Leiden~\citep{traag-leiden}) on both the synthetic and real graphs and compare the resulting partitions.
They answer the question whether \emph{the community-detection algorithms behave the same way on synthetic graphs as they do on the real graphs}.
These metrics take only the graph as input; they are ``blind'' to the planted labels. We argue that this way of comparing graphs that are to serve as community detection benchmarks is better-fitted to the task. By comparing performance of established solutions, we can check if the synthetic outputs present, for example, the same biases on both input and output graphs, without the need to consult external and potentially noisy ``declared'' labels.






\subsection{Statistical pipeline}\label{sec:stats}

Our evaluation employs a practical pipeline for comparing all algorithms whilst hoping to retain some statistical elegance.

\paragraph{Stage 1: Friedman omnibus test.}
For each dataset, the 12~methods are ranked from 1 (best) to 12 (worst) based on their mean distance across 50~independent samples on all retained metrics. The Friedman test checks whether the observed mean ranks are consistent with the null hypothesis that all methods perform identically. It reports the $\chi^2$ statistic and corresponding $p$-value; rejection indicates that at least one method differs significantly.

\paragraph{Stage 2: Mann-Whitney U tests.}
Since the results in each block (dataset, metric) contain potentially dependent values (because, e.g., average path lengths are necessarily correlated with longest path lengths), we cannot run standard statistical procedures using $N=182$ samples. On the other hand, on $N=7$ datasets we do not expect the Nemenyi critical difference diagram or the Wilcoxon signed-rank test to indicate significant differences between any pair of algorithms. Instead, we compare the $50$ results obtained by each pair of algorithms on each (dataset, metric) cell and report wins and ties as computed using the Mann-Whitney U test with uncorrected $p < 0.05$. While these task-level counts are not substitutes for global significance claims, they provide a rigorous, descriptive breakdown of exactly where and how frequently each model outperforms the baselines. To remove impact of scale, all values in a given (dataset, metric) cell are standardised prior to aggregation. This has no impact on method ranks.

To quantify uncertainty in the mean rank estimates, we additionally report 95\% bootstrap confidence intervals for each method's mean rank. The intervals are obtained by block-resampling (dataset, metric) rows with replacement (10,000 draws) and recording the 2.5th and 97.5th percentiles of the resulting distribution of mean ranks. Because this procedure resamples the atomic evaluation unit -- the (dataset, metric) block -- it correctly propagates both dataset-level and metric-level variance without assuming independence across blocks.

\paragraph{Large-graph handling.}~\label{par:large_graph}
For the three largest datasets (Cit-Patents, DBLP, OGBN-ArXiv), several metrics are computationally prohibitive on the full graph.
We compute these on subgraphs of up to 50,000~nodes obtained via BFS from random seed nodes.
Computationally heavy metrics (e.g., average path length, betweenness centrality) are estimated from 2,000~sampled node pairs or paths.
The same subsampling procedure is applied identically to both the real and synthetic graphs, ensuring that any approximation error cancels in the distance computation.


\clearpage
\subsection{Evaluation design}\label{sec:design}

Table~\ref{tab:design_summary} summarises the experimental design.

\begin{table}[t!]
\caption{Summary of the experimental design.}
\label{tab:design_summary}
\centering
\small
\begin{tabular}{lr}
\toprule
Component & Count \\
\midrule
Datasets & $7$ \\
Methods (5 base $\times$ 2 variants + 2 CS) & $12$ \\
Metrics & $26$ \\
Metric categories & $6$ \\
Samples per method per dataset & $50$ \\
(dataset, metric) blocks& $7 \times 26 = 182$ \\
(dataset, metric) blocks (non-endogenous) & $7 \times 20 = 140$ \\
\bottomrule
\end{tabular}
\end{table}

The five classical generators are evaluated in two configurations: standard (as published) and near-DAG (Section~\ref{sec:neardag}).
This doubling is not an artefact of the comparison but a deliberate design choice that allows us to address two questions simultaneously:
(1)~how do the generators compare to each other, and
(2)~how does cycle breaking affect each generator's fidelity?
Together with CS and CS\,(DAG), this gives $k = 12$~methods.

All methods receive the same input: the real graph's adjacency matrix and community labels (where applicable).
CS and the block models (SBM, DC-SBM) use community labels; the Configuration Model and ER use only degree or density statistics; LFR uses global structural parameters estimated from the real graph.
This heterogeneity in input is inherent to the methods and is reflected in the parsimony analysis (Section~\ref{sec:parsimony}). For two datasets: DBLP and OGBN-ArXiv, real timestamps are used when searching for the set of back-edges. The remaining datasets are first equipped with an approximate topological ordering based on the greedy Eades heuristic~\cite{Eades1993}. The cit-Patents networks has missing timestamps for nearly $1/3$ of nodes, so the real timestamps were discarded in favor of the heuristic as well.
Let us also note that there exists an asymmetry in back-edge placement between CS and cycle breaking of reference methods that results from one process being model specific and second model-agnostic; to alleviate potential issues in comparison, we separate the analysis of impact of adding back-edges into CS from adding them to reference methods.


\section{Results}\label{sec:results}

We organise the results of our benchmark into six subsections.
We first present the global ranking of all 12~methods (Section~\ref{sec:global}), then dissect it by structural category (Section~\ref{sec:category}) and by the endogenous/exogenous distinction (Section~\ref{sec:nonendo}) introduced in Section~\ref{sec:endo_exo}.
Section~\ref{sec:ablation} isolates the contribution of the back-edge mechanism through an ablation study.
Section~\ref{sec:perdataset} examines per-dataset variation to identify where different methods succeed and fail.
Finally, Section~\ref{sec:parsimony} relates performance to parameter complexity.


\subsection{Global comparison}\label{sec:global}

Figures~\ref{fig:rank_dotplot}, \ref{fig:pairwise_heat}, and Table~\ref{tab:mean_ranks} summarise the global ranking of all 12~methods.
The Friedman omnibus test~\citep{friedman1937} rejects the null hypothesis that all methods perform identically ($\chi^2 = 21.1$, $p < 0.033$, $N=7$).

The ranking reveals a three-tier structure. High-parameter descriptive models and CS form the top tier, outperforming mid-tier structure-agnostic models, while models with constant parameter counts sit at the bottom.

Several observations deserve emphasis.
First, the top cluster contains both high-parameter descriptive models (DC-SBM-nD with $O(N + k^2)$ parameters) and low-parameter models (CS with $O(k)$), suggesting that parameter count alone does not determine structural fidelity on this task.
Second, cycle breaking improves every baseline's mean rank with improvements ranging from insignificant (CM, LFR) to notable (DC-SBM, SBM, ER).
Third, we observe that models with constant numbers of parameters (ER, LFR) perform significantly worst. This indicates that the complex nature of citation networks cannot be properly encapsulated by a small set of values.

The $\Delta$ column in Table~\ref{tab:mean_ranks} records the rank shift when endogenous metrics are excluded (Section~\ref{sec:nonendo}).
A consistent pattern emerges: methods that encode ground-truth community structure -- DC-SBM, DC-SBM-nD, SBM, SBM-nD -- all worsen.
Methods without explicit input community encoding improve or remain stable: Config~Model, Config~Model-nD, ER, CS. This systematic pattern motivates the non-endogenous analysis.



\begin{table}[tb!]
\centering
\caption{Mean ranks across 26 retained metrics ($N=182$ blocks) and the
20 non-endogenous subset ($N=140$ blocks), with 95\% bootstrap
confidence intervals. $\Delta$ is the rank change when endogenous metrics are excluded (negative\,=\,improvement). See Figure~\ref{fig:pairwise_heat} for pairwise comparisons.}
\label{tab:mean_ranks}
\small
\begin{tabular}{l
                S[table-format=1.2]
                c
                S[table-format=1.2]
                c
                S[table-format=+1.2,print-implicit-plus=true]}
\toprule
 & \multicolumn{2}{c}{All 26 metrics}
 & \multicolumn{2}{c}{20 non-endogenous}
 & \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Method & Rank & 95\,\% CI & Rank & 95\,\% CI & $\Delta$ \\
\midrule
    DC-SBM-nD & 5.21 & [4.77,\,5.66] & 5.77 & [5.26,\,6.29] & +0.56 \\
    \textbf{CS} & 5.48 & [5.02,\,5.93] & 5.27 & [4.73,\,5.84] & -0.21 \\
    DC-SBM & 5.48 & [5.01,\,5.96] & 6.18 & [5.66,\,6.69] & +0.70 \\
    \midrule
    Config Model-nD & 6.04 & [5.58,\,6.50] & 5.51 & [5.00,\,6.04] & -0.52 \\
    Config Model & 6.05 & [5.58,\,6.54] & 5.64 & [5.13,\,6.16] & -0.41 \\
    SBM-nD & 6.30 & [5.87,\,6.73] & 6.73 & [6.25,\,7.19] & +0.43 \\
    \textbf{CS (DAG)} & 6.40 & [5.85,\,6.94] & 6.09 & [5.46,\,6.71] & -0.31 \\
    SBM & 6.55 & [6.10,\,7.02] & 7.01 & [6.51,\,7.52] & +0.46 \\
    \midrule
    LFR-nD & 6.93 & [6.46,\,7.40] & 7.04 & [6.46,\,7.63] & +0.11 \\
    LFR & 6.97 & [6.45,\,7.50] & 7.29 & [6.66,\,7.94] & +0.32 \\
    ER-nD & 7.98 & [7.47,\,8.49] & 7.39 & [6.81,\,7.97] & -0.60 \\
    ER & 8.60 & [8.10,\,9.09] & 8.07 & [7.49,\,8.66] & -0.53 \\\bottomrule
\end{tabular}
\end{table}

\begin{figure}[p!]
\centering
\includegraphics[width=\textwidth]{figs/fig_rank_dotplot.pdf}
\caption{Global mean ranks with 95\% bootstrap confidence intervals,
obtained by block-resampling (dataset\,$\times$\,metric) rows with
replacement ($B = 10{,}000$ draws). Point estimates are shown as
diamonds~({\footnotesize$\blacklozenge$}) for CS variants and
circles~({\footnotesize$\bullet$}) for baselines; horizontal bars span
the 2.5th-97.5th percentile of the bootstrap distribution. The dashed
vertical line marks the median rank (6.5) for $k=12$ methods. Left
panel: all 26 metrics ($N=182$ blocks); right panel: 20 non-endogenous
metrics ($N=140$ blocks).}
\label{fig:rank_dotplot}
\end{figure}

\begin{figure}[p!]
\centering
\includegraphics[width=0.8\textwidth]{figs/fig_pairwise_heat.pdf}
\caption{Pairwise comparison: number of CS wins / ties / losses against
its six nearest competitors, computed via uncorrected Mann-Whitney U
test ($\alpha = 0.05$) on the 50 runs per (dataset, metric) block.
Cell colour encodes CS's win rate (green ${>}50\%$ = CS advantage;
red ${<}50\%$ = competitor advantage). Left column: all 26 metrics
($N=182$ blocks); right column: 20 non-endogenous metrics ($N=140$
blocks).}
\label{fig:pairwise_heat}
\end{figure}


\subsection{Category-level analysis}\label{sec:category}


\begin{table}[t!]
\centering
\caption{Category-level performance scores (higher~=~better):
$(\,k{+}1 - \bar{r}\,)/k$ where $\bar{r}$ is the mean rank and $k=12$ (see Figure~\ref{fig:category_radar} for visual comparison).}
\label{tab:category_scores}
\small
\begin{tabular}{l *{6}{S[table-format=1.3]}}
\toprule
Method & \rotatebox{60}{\small Global Topology} & \rotatebox{60}{\small Degree Structure} & \rotatebox{60}{\small Meso. Endogenous} & \rotatebox{60}{\small Meso. Exogenous} & \rotatebox{60}{\small Local Structure} & \rotatebox{60}{\small Flow \& Connectivity} \\
\midrule
    \textbf{CS} & 0.587 & 0.658 & 0.569 & 0.591 & 0.732 & 0.671 \\
    \textbf{CS (DAG)} & \textbf{0.655} & 0.524 & 0.464 & 0.464 & 0.667 & 0.671 \\
    DC-SBM-nD & 0.524 & \textbf{0.708} & 0.806 & 0.516 & \textbf{0.795} & 0.456 \\
    DC-SBM & 0.512 & 0.539 & \textbf{0.819} & 0.571 & 0.756 & 0.409 \\
    Config Model-nD & 0.651 & 0.664 & 0.434 & 0.579 & 0.458 & \textbf{0.853} \\
    Config Model & 0.611 & 0.691 & 0.464 & 0.571 & 0.467 & 0.790 \\
    SBM-nD & 0.452 & 0.580 & 0.679 & 0.605 & 0.423 & 0.484 \\
    SBM & 0.381 & 0.527 & 0.665 & \textbf{0.623} & 0.434 & 0.417 \\\bottomrule
\end{tabular}
\end{table}

\begin{figure}[t!]
\centering
\includegraphics[width=0.8\textwidth]{figs/fig_category_radar.pdf}
\caption{Category-level performance scores for selected methods.
Score $= (k{+}1 - \bar{r})/k$, where $\bar{r}$ is the category mean rank and $k = 12$.
Higher is better; 0.5 indicates median performance.}
\label{fig:category_radar}
\end{figure}


The global rank averages results over structurally diverse metrics and inevitably masks important more granular category-level variation. Figure~\ref{fig:category_radar} and Table~\ref{tab:category_scores} decompose performance into six structural categories. Category scores are defined as $s = (k{+}1 - \bar{r})/k$ where $\bar{r}$ is the method's mean rank within the category and $k = 12$.
The central finding is that no single method dominates all categories.
The category leaders are:

\begin{itemize}[nosep]
\item \textbf{Global Topology:} Growth-based DAG construction and degree-preserving rotation both produce realistic distance/diameter structure.
\item \textbf{Degree Structure:} DC-SBM and Config~Model both preserve the input's degree sequence by construction and are expected to dominate this category; CS's growth process approximates it from community-dependent parameters.
\item \textbf{Meso.~Endogenous:} The top models directly encode the ground-truth block structure with $O(N + k^2)$ parameters.
SBM-nD and SBM also score well, reflecting their explicit community parametrisation.
\item \textbf{Meso.~Exogenous:} DC-SBM-nD drops to 0.516, noticeably below the methods it dominates on endogenous metrics. Here SBM variants and CS take the lead. This reversal is the empirical basis for the endogenous vs~exogenous distinction: memorising the ground-truth community structure does not guarantee that algorithms will perceive the synthetic graph similarly to the real one.
\item \textbf{Local Structure:} Degree-preservation coupled with granular inter- and intra-cluster density reconstruction are likely forcing similar local patterns as in the input graph, driving the notable lead over the competition. We note the good performance of CS despite no parameters directly encoding local structure of nodes.
\item \textbf{Flow \& Connectivity:} The Configuration~Model's exact degree preservation combined with topological rotation produces highly realistic flow structure. DC-SBM-nD scores only 0.456: static block models have no native mechanism for generating meaningful flow.
\end{itemize}

The category landscape reveals a fundamental trade-off.
High-parameter models with explicit community encoding (DC-SBM, SBM) dominate endogenous mesoscopic metrics but underperform on flow and connectivity.
Structure-agnostic models (Config~Model) excel at degree and flow fidelity but have no community awareness required to replicate input's heterogeneity.
Growth-based models (CS, CS\,(DAG)) occupy a firm middle ground, with competitive performance across all categories and excelling in replicating the challenges input graphs pose for community detection algorithms (Meso.~Exogenous). CS is also notable for its \emph{balance}: its minimum category score is 0.569 (Meso.~Endogenous), making it the only method whose worst category exceeds 0.47. This balance means CS is a reasonable default when the downstream task's structural requirements are not known in advance.


\subsection{Non-endogenous analysis}\label{sec:nonendo}

In this section, we turn our attention back to the $\Delta$ column in Table~\ref{tab:mean_ranks} and the 20-metric ranks already reported there. When the 6~endogenous metrics are excluded, the ranking shifts substantially for several methods:
\begin{itemize}[nosep]
\item DC-SBM-nD worsens from 5.21 to 5.77 ($\Delta = +0.56$);
\item DC-SBM worsens from 5.48 to 6.18 ($\Delta = +0.70$);
\item Config~Model-nD improves from 6.04 to 5.51 ($\Delta = -0.52$);
\item CS improves from 5.48 to 5.27 ($\Delta = -0.21$).
\end{itemize}

On the 20 non-endogenous metrics, CS~(5.27) and Config~Model-nD~(5.51) emerge as the top two methods, while DC-SBM-nD drops to fourth (5.77).
The gap between CS and DC-SBM-nD reverses from $-0.27$ (full) to $+0.50$ (non-endogenous). Notably, out of the $42$ evaluation blocks removed, the Win–Tie–Loss ratio of DC-SBM-nD to CS was $32-1-9$. This indicates that the largest advantage of DC-SBM-nD lied in this group, since the resulting Win–Tie–Loss ratio of the two algorithms is $59$-$9$-$72$.

The systematic nature of the shift is more informative than any individual gap.
Every method with explicit community parametrisation (DC-SBM, DC-SBM-nD, SBM, SBM-nD) worsens when endogenous metrics are removed.
Every method without it (Config~Model, ER, CS) improves or remains stable. The exception here is LFR which also degrades despite encoding only general parameters. These observations are consistent with the hypothesis that endogenous metrics reward memorisation of planted statistics, while exogenous metrics reward functional realism: the ability to produce a graph on which community-detection algorithms behave as they do on the real network.
Both perspectives are valid evaluation criteria; we argue that for the specific use case of community-detection benchmarking, exogenous metrics are the primary concern.


\subsection{Ablation: Cycle breaking}\label{sec:ablation}

Let us consider how cycle breaking impacts the reference methods' performance in each category, and how removing back-edges impacts CS.

From Figure~\ref{fig:heatmap}, we see that the per-category scores present clear trends. As a process, cycle breaking allows almost all reference methods to replicate the input graph better in terms of Global Topology, Degree Structure, and Flow \& Connectivity. However, it has varied impact on local structure (from significant downgrades to notable improvements), mesoscopic endogenous structure (albeit the results indicate small changes, if any), but greatly negatively impacting mesoscopic exogenous similarity to the input graph.

These results indicate an inevitable and problematic trade-off: existing static methods cannot simultaneously recreate the graph's structure from the perspective of a community detection algorithm while correctly preserving flow  and degree structures inherent to citation-like networks.

\begin{figure}[t!]
    \centering
    \includegraphics[width=0.8\textwidth]{figs/fig_neardag_heatmap.pdf}
    \caption{Heatmap presenting impact of cycle breaking per category. Each cell represents a percent of instance a near-DAG version of the method achieved better results than the standard method on the corresponding metrics.}
    \label{fig:heatmap}
\end{figure}

\begin{figure}[t!]
\centering
\includegraphics[width=0.50\textwidth]{figs/fig_ablation.pdf}
\caption{Ablation: effect of back-edge injection on category scores.
Positive differences (annotated) indicate categories where CS outperforms the pure DAG variant.}
\label{fig:ablation}
\end{figure}

\begin{table}[t]
\centering
\caption{Ablation: CS vs~CS (DAG).
``Wins'' counts (dataset $\times$ metric) cells with lower distance.
Back-edges improve degree structure and mesoscopic fidelity at the cost of global topology. The latter values stand for Score as introduced in Section~\ref{sec:category}}
\label{tab:ablation}
\small
\begin{tabular}{l c S[table-format=1.3] S[table-format=1.3]}
\toprule
Category & DAG wins & {CS} & {DAG} \\
\midrule
    Global Topology & 15/21 & 0.587 & \textbf{0.655} \\
    Degree Structure & 7/28 & \textbf{0.658} & 0.524 \\
    Meso.~Endogenous  & 14/42 & \textbf{0.569} & 0.464 \\
    Meso.~Exogenous & 10/42 & \textbf{0.591} & 0.464 \\
    Local Structure & 7/28 & \textbf{0.732} & 0.667 \\
    Flow \& Connectivity & 10/21 & 0.671 & 0.671 \\\bottomrule
\end{tabular}
\end{table}

To isolate the contribution of community-aware back-edge injection, we compare CS against CS~(DAG); see Figure~\ref{fig:ablation} and Table~\ref{tab:ablation}. The overall rank $\Delta$ is 0.92, which indicates practical difference and shows clear category-specific patterns.

Back-edges help on four categories.
The largest effect is on Meso.~Exogenous, where CS wins in 32 of 42 dataset$\times$metric cells: the short-range cycles introduced by back-edges make community-detection algorithms perceive the graph more realistically. Degree Structure (21/28), Meso.~Endogenous (28/42), and Local Structure (21/28) also improve, because back-edges add the small feedback loops frequent in citation networks (small cycles, revision-induced references).

Back-edges hurt in one category: Global Topology degrades significantly (CS wins only 6/21), as back-edges shorten effective diameters and average path lengths which the estimated parameters aimed to reproduce. Flow \& Connectivity does not seem to show any change.

This trade-off has a practical implication: the choice between the variants should be task-driven. For community-detection benchmarking, CS with back-edges is preferred. For tasks sensitive to flow structure (influence propagation, temporal ordering), CS\,(DAG) is likely the better choice. Notably, this trade-off mirrors the pattern observed in cycle breaking of baselines (Section~\ref{sec:neardag}): any transformation that introduces or removes cycles shifts the balance between mesoscopic/local fidelity and flow fidelity.



\subsection{Per-dataset variation}\label{sec:perdataset}

\begin{figure}[t]
\centering
\includegraphics[width=\textwidth]{figs/fig_per_dataset.pdf}
\caption{Per-dataset performance scores for CS, CS\,(DAG), and DC-SBM-nD.
Left: all 26~metrics; right: 20~non-endogenous metrics.
Score $= (k{+}1 - \bar{r})/k$ averaged within each dataset.}
\label{fig:per_dataset}
\end{figure}

Now we shall focus on the comparison of our algorithm to the main competitor in terms of general performance, i.e., DC-SBM-nD. Figure~\ref{fig:per_dataset} shows the performance of the three methods.

The most striking pattern is that \emph{relative performance depends on dataset characteristics}.
CS shows advantage on Cora-Full and OGBN-ArXiv -- medium-scale networks with moderate community counts (70 and 40) where the Price-Pareto assumptions hold well. DC-SBM-nD exhibits a better performance on DBLP and PubMed. DBLP is the largest network in our evaluation, where the uniform inter-community assumption becomes most problematic; PubMed has only 3~communities, limiting the Price-Pareto model's degrees of freedom. On Cit-Patents -- the second largest network -- DC-SBM-nD leads, but the difference in score does not seem significant, demonstrating that scale alone does not determine CS's performance; rather, the interaction between scale and community heterogeneity is the key factor. Notably, the theoretical submission introducing the model on which CS is built introduces a variant taking into account ageing of the nodes, albeit we omit it due to the need for numerical estimation of parameters. As we observe though, CS remains highly competitive even on large network where the ageing effect is typically observed.

On the small benchmarks (Cora, CiteSeer), DC-SBM-nD and CS are comparable, with neither showing a consistent advantage.

The non-endogenous panel (right) shifts the picture.
DC-SBM-nD beats both variants of CS only on one dataset (DBLP). This confirms that DC-SBM-nD's overall edge in the full evaluation is partly attributable to its endogenous advantage, which is expected given its direct encoding of ground-truth community statistics.


\subsection{The parsimony argument}\label{sec:parsimony}

\begin{figure}[t!]
\centering
\includegraphics[width=\textwidth]{figs/fig_parsimony.pdf}
\caption{Performance-parsimony trade-off.
Horizontal axis: geometric mean of parameter counts across the 7~datasets (log scale).
Vertical axis: mean rank (lower is better).
Left: all 26~metrics; right: 20~non-endogenous metrics.}
\label{fig:parsimony}
\end{figure}

The preceding sections establish \emph{what} the methods achieve; this section asks what they achieve \emph{relative to their complexity}.
Figure~\ref{fig:parsimony} plots mean rank against the geometric mean of parameter counts across the seven datasets.

The left panel (26~metrics) reveals that the top-cluster methods occupy vastly different positions on the parameter axis.
DC-SBM-nD~(5.21) and DC-SBM~(5.48) require $O(N + k^2)$, Config~Model variants require $O(N)$, CS~(5.48) requires $4k$: 28~on Cora, 1672~on Cit-Patents, 251,616~on DBLP.
The ratio between parameter counts of DC-SBM-nD and CS exceeds $1{,}750:1$ on Cit-Patents and $15{,}740:1$ on DBLP.

The right panel (20~non-endogenous) sharpens the picture.
CS~(5.27) moves into the Pareto-optimal position: no method achieves both a better rank and fewer parameters.
Config~Model-nD~(5.51) achieves a similar rank with $O(N)$ parameters, but it produces no community structure -- an essential requirement for community-detection benchmarking.
Among community-aware methods, CS uniquely combines competitive fidelity with minimal parametrisation.

This parsimony gap is not merely a storage difference.
It reflects a qualitative distinction between \emph{descriptive} models that parametrise a specific graph (DC-SBM encodes each node's expected degree and each block's connection probability) and \emph{mechanistic} models that parametrise a growth process (CS encodes $p_i$, $m_i$, $\rho_i$, $\sigma^2_i$ per community).
The former can reproduce one graph faithfully; the latter can generate a family of structurally similar graphs from interpretable assumptions about how citations occur.




\section{Conclusion}\label{sec:conclusion}

The synthetic generation of nearly directed, nearly acyclic graphs with planted communities has long been an underserved area in information sciences, severely limiting our ability to benchmark algorithms on citation-like topologies. In this work, we addressed this gap through three primary contributions: the introduction of the CS generator, evaluation of cycle breaking as a transformation applied to static reference generators, and separate validation in terms of endogenous and exogenous mesoscopic structures for detailed results. We believe our contributions sheds new light on the task of generating nearly acyclic directed graphs: while DC-SBM remains most competitive in terms of network replication, it is not dominant in terms of specific categories and underdelivers when it comes to replicating community detection algorithm performance. Moreover, our CS offers the same quality of synthetic graphs with better fits to exogenous mesoscopic similarity for the fraction of the price -- measured in terms of parameters fitted. Our analysis also shows that cycle breaking as a process generally helps all algorithms fit to the input citation networks better but it comes at a price of worse community recreation which is an important caveat when evaluating community detection. Notably, these observations could not be made if not for the dichotomous methodology we employed for validating mesoscopic fits.

Ultimately, parsimony in network modelling is not a concession, but a feature. CS demonstrates that an interpretable, mathematically elegant growth process can match the generative fidelity of highly parametrised descriptive models, providing a robust new foundation for the study and simulation of citation networks.

Still, we should clearly acknowledge its theoretical and methodological boundaries.
First, the current Price-Pareto model lacks a mechanism for attention decay. Consequently, CS's in-degree fidelity degrades on massive networks with deep temporal histories. Integrating attention decay is theoretically possible, but doing so requires numerical parameter estimation, thereby sacrificing the analytical tractability that is CS's primary advantage.
Second, the model assumes that accidental citations are distributed uniformly across all communities. In reality, interdisciplinary citation patterns are highly heterogeneous (e.g., machine learning papers cite statistics much more frequently than they cite history). Allowing for non-uniform inter-community citation rates would accurately capture this, but it would require an $O(k^2)$ parameter matrix, converging toward the parameter bloat of standard block models.

Methodologically, our evaluation is constrained by the scarcity of suitable datasets. With only seven networks representing the comprehensive collection of directed near-DAGs with ground-truth communities, our statistical power is inherently limited; mean rank differences of 0.3 to 0.5, while directionally informative, cannot reach formal significance. We have considered two additional data sources that were ultimately omitted: OpenAlex (no consensus in research community about which subgraph take as representative) and APS citation network (limited availability and usage restrictions).

These limitations naturally motivate our future work. Algorithmically, we will aim to incorporate the ageing coefficient into CS without sacrificing the interpretability and time complexity of the generator. We believe that thanks to CS's ability to replicate real networks, we can draw meaningful conclusions about network phenomena using CS as a statistical experiment ground, which could allow us to reach new conclusions that are unavailable with a limited selection of real-world datasets. Theoretically, exploring non-uniform inter-community citation rates and integrating the numerical attention-decay derivations remain active avenues for refining the underlying generative process.


\section*{Software and Data Availability}
The CS generator is released as open-source software at \url{https://github.com/lukaszbrzozowski/CitationSeeder}.

The reproduction pipeline is available at \url{https://github.com/lukaszbrzozowski/CDSI_DAG}.

The UnPACD software used to process all datasets is available at \url{https://github.com/lukaszbrzozowski/unpacd}.

\printcredits

\section*{Declaration of Generative AI and AI-assisted technologies in the writing process}
During the preparation of this work the first author used Claude (Anthropic) for code generation of analysis scripts.
The authors reviewed and edited all output and take full responsibility for the content of this publication.



\bibliographystyle{cas-model2-names}

\begin{thebibliography}{51}
\expandafter\ifx\csname natexlab\endcsname\relax\def\natexlab#1{#1}\fi
\providecommand{\url}[1]{\texttt{#1}}
\providecommand{\href}[2]{#2}
\providecommand{\path}[1]{#1}
\providecommand{\DOIprefix}{doi:}
\providecommand{\ArXivprefix}{arXiv:}
\providecommand{\URLprefix}{URL: }
\providecommand{\Pubmedprefix}{pmid:}
\providecommand{\doi}[1]{\href{http://dx.doi.org/#1}{\path{#1}}}
\providecommand{\Pubmed}[1]{\href{pmid:#1}{\path{#1}}}
\providecommand{\bibinfo}[2]{#2}
\ifx\xfnm\relax \def\xfnm[#1]{\unskip,\space#1}\fi
\bibitem[{Abbe(2018)}]{emmanuel_abb__11402603}
\bibinfo{author}{Abbe, E.}, \bibinfo{year}{2018}.
\newblock \bibinfo{title}{Community detection and stochastic block models:
  Recent developments}.
\newblock \bibinfo{journal}{Journal of Machine Learning Research}
  \bibinfo{volume}{18}, \bibinfo{pages}{1--86}.
\bibitem[{Abbé and Sandon(2016)}]{emmanuel_abb__8011b685}
\bibinfo{author}{Abbé, E.}, \bibinfo{author}{Sandon, C.},
  \bibinfo{year}{2016}.
\newblock \bibinfo{title}{Achieving the {KS} threshold in the general
  {S}tochastic {B}lock {M}odel with linearized acyclic belief propagation}, in:
  \bibinfo{booktitle}{Proc. Neural Information Processing Systems (NIPS'16)},
  pp. \bibinfo{pages}{1334--1342}.
\bibitem[{Albert and Barab\'asi(2002)}]{BA-model}
\bibinfo{author}{Albert, R.}, \bibinfo{author}{Barab\'asi, A.L.},
  \bibinfo{year}{2002}.
\newblock \bibinfo{title}{Statistical mechanics of complex networks}.
\newblock \bibinfo{journal}{Reviews of Modern Physics} \bibinfo{volume}{74},
  \bibinfo{pages}{47--97}.
\newblock \DOIprefix\doi{10.1103/RevModPhys.74.47}.
\bibitem[{Bertoli-Barsotti et~al.(2024)Bertoli-Barsotti, Gagolewski, Siudem and
  Żogała Siudem}]{lucio}
\bibinfo{author}{Bertoli-Barsotti, L.}, \bibinfo{author}{Gagolewski, M.},
  \bibinfo{author}{Siudem, G.}, \bibinfo{author}{Żogała Siudem, B.},
  \bibinfo{year}{2024}.
\newblock \bibinfo{title}{Equivalence of inequality indices in the
  three-dimensional model of informetric impact}.
\newblock \bibinfo{journal}{Journal of Informetrics} \bibinfo{volume}{18},
  \bibinfo{pages}{101566}.
\newblock \DOIprefix\doi{10.1016/j.joi.2024.101566}.
\bibitem[{Bianconi and Barabási(2001)}]{BB-model}
\bibinfo{author}{Bianconi, G.}, \bibinfo{author}{Barabási, A.L.},
  \bibinfo{year}{2001}.
\newblock \bibinfo{title}{Competition and multiscaling in evolving networks}.
\newblock \bibinfo{journal}{Europhysics Letters} \bibinfo{volume}{54},
  \bibinfo{pages}{436}.
\newblock \DOIprefix\doi{10.1209/epl/i2001-00260-6}.
\bibitem[{Bojchevski and G{\"u}nnemann(2018)}]{bojchevsky}
\bibinfo{author}{Bojchevski, A.}, \bibinfo{author}{G{\"u}nnemann, S.},
  \bibinfo{year}{2018}.
\newblock \bibinfo{title}{Deep {G}aussian embedding of graphs: {U}nsupervised
  inductive learning via ranking}, in: \bibinfo{booktitle}{International
  Conference on Learning Representations (ICLR'18)}.
\bibitem[{Bollobás(1980)}]{cm1980}
\bibinfo{author}{Bollobás, B.}, \bibinfo{year}{1980}.
\newblock \bibinfo{title}{A probabilistic proof of an asymptotic formula for
  the number of labelled regular graphs}.
\newblock \bibinfo{journal}{European Journal of Combinatorics}
  \bibinfo{volume}{1}, \bibinfo{pages}{311–316}.
\newblock \DOIprefix\doi{10.1016/S0195-6698(80)80030-8}.
\bibitem[{Bonifati et~al.(2020)Bonifati, Holubová, Prat-Pèrez and
  Sakr}]{angela_bonifati_9f84e862}
\bibinfo{author}{Bonifati, A.}, \bibinfo{author}{Holubová, I.},
  \bibinfo{author}{Prat-Pèrez, A.}, \bibinfo{author}{Sakr, S.},
  \bibinfo{year}{2020}.
\newblock \bibinfo{title}{Graph generators}.
\newblock \bibinfo{journal}{ACM Computing Surveys} \bibinfo{volume}{53},
  \bibinfo{pages}{1--30}.
\newblock \DOIprefix\doi{10.1145/3379445}.
\bibitem[{Brisson et~al.(2025)Brisson, Bothorel and Duminy}]{brisson2025}
\bibinfo{author}{Brisson, L.}, \bibinfo{author}{Bothorel, C.},
  \bibinfo{author}{Duminy, N.}, \bibinfo{year}{2025}.
\newblock \bibinfo{title}{{DynBenchmark}: {C}ustomizable ground truths to
  benchmark community detection and tracking in temporal networks}, in:
  \bibinfo{booktitle}{Proc. France's International Conference on Complex
  Systems (FRCCS 2025)}, pp. \bibinfo{pages}{74--85}.
\newblock \DOIprefix\doi{10.1007/978-3-032-00206-8_8}.
\bibitem[{Brzozowski(2026)}]{unpacd}
\bibinfo{author}{Brzozowski, L.}, \bibinfo{year}{2026}.
\newblock \bibinfo{title}{{UnPACD}: Unified patent and citation dataset}.
\newblock
  \bibinfo{howpublished}{\url{https://github.com/lukaszbrzozowski/unpacd}}.
\bibitem[{Brzozowski et~al.(2026)Brzozowski, Gagolewski, Siudem and Żogała
  Siudem}]{brzozowski2025pricepareto}
\bibinfo{author}{Brzozowski, L.}, \bibinfo{author}{Gagolewski, M.},
  \bibinfo{author}{Siudem, G.}, \bibinfo{author}{Żogała Siudem, B.},
  \bibinfo{year}{2026}.
\newblock \bibinfo{title}{The {P}rice-{P}areto growth model of networks with
  community structure} \DOIprefix\doi{10.48550/arxiv.2510.13392}.
  \bibinfo{note}{under review (preprint)}.
\bibitem[{Caltagirone et~al.(2017)Caltagirone, Lelarge and
  Miolane}]{caltagirone2017}
\bibinfo{author}{Caltagirone, F.}, \bibinfo{author}{Lelarge, M.},
  \bibinfo{author}{Miolane, L.}, \bibinfo{year}{2017}.
\newblock \bibinfo{title}{Recovering asymmetric communities in the {S}tochastic
  {B}lock {M}odel}.
\newblock \bibinfo{journal}{IEEE Transactions on Network Science and
  Engineering} \bibinfo{volume}{5}, \bibinfo{pages}{237--246}.
\newblock \DOIprefix\doi{10.1109/tnse.2017.2758201}.
\bibitem[{Carballo-Castro et~al.(2026)Carballo-Castro, Madeira, QIN, Thanou and
  Frossard}]{alba_carballo_castro_fa8c0641}
\bibinfo{author}{Carballo-Castro, A.}, \bibinfo{author}{Madeira, M.},
  \bibinfo{author}{QIN, Y.}, \bibinfo{author}{Thanou, D.},
  \bibinfo{author}{Frossard, P.}, \bibinfo{year}{2026}.
\newblock \bibinfo{title}{Generating directed graphs with dual attention and
  asymmetric encoding}, in: \bibinfo{booktitle}{The Fourteenth International
  Conference on Learning Representations}.
\bibitem[{Chang and Blei(2009)}]{rtm-model}
\bibinfo{author}{Chang, J.}, \bibinfo{author}{Blei, D.}, \bibinfo{year}{2009}.
\newblock \bibinfo{title}{Relational topic models for document networks}, in:
  \bibinfo{editor}{van Dyk, D.}, \bibinfo{editor}{Welling, M.} (Eds.),
  \bibinfo{booktitle}{Proceedings of the Twelfth International Conference on
  Artificial Intelligence and Statistics}, pp. \bibinfo{pages}{81--88}.
\bibitem[{Chen et~al.(2022)Chen, Yu, Yang and Shao}]{chen2022}
\bibinfo{author}{Chen, H.}, \bibinfo{author}{Yu, Z.}, \bibinfo{author}{Yang,
  Q.}, \bibinfo{author}{Shao, J.}, \bibinfo{year}{2022}.
\newblock \bibinfo{title}{Community detection in subspace of attribute}.
\newblock \bibinfo{journal}{Information Sciences} \bibinfo{volume}{602},
  \bibinfo{pages}{220--235}.
\newblock \DOIprefix\doi{10.1016/j.ins.2022.04.047}.
\bibitem[{Decelle et~al.(2011)Decelle, Krząkała, Moore and
  Zdeborová}]{aur_lien_decelle_6fcd1196}
\bibinfo{author}{Decelle, A.}, \bibinfo{author}{Krząkała, F.},
  \bibinfo{author}{Moore, C.}, \bibinfo{author}{Zdeborová, L.},
  \bibinfo{year}{2011}.
\newblock \bibinfo{title}{Asymptotic analysis of the {S}tochastic {B}lock
  {M}odel for modular networks and its algorithmic applications}.
\newblock \bibinfo{journal}{Physical Review E} \bibinfo{volume}{84}.
\newblock \DOIprefix\doi{10.1103/physreve.84.066106}.
\bibitem[{Drobyshevskiy and Turdakov(2019)}]{Drobyshevskiy-survey}
\bibinfo{author}{Drobyshevskiy, M.}, \bibinfo{author}{Turdakov, D.},
  \bibinfo{year}{2019}.
\newblock \bibinfo{title}{Random graph modeling: {A} survey of the concepts}.
\newblock \bibinfo{journal}{ACM Computing Surveys} \bibinfo{volume}{52},
  \bibinfo{pages}{131}.
\newblock \DOIprefix\doi{10.1145/3369782}.
\bibitem[{Eades et~al.(1993)Eades, Lin and Smyth}]{Eades1993}
\bibinfo{author}{Eades, P.}, \bibinfo{author}{Lin, X.}, \bibinfo{author}{Smyth,
  W.}, \bibinfo{year}{1993}.
\newblock \bibinfo{title}{A fast and effective heuristic for the feedback arc
  set problem}.
\newblock \bibinfo{journal}{Information Processing Letters}
  \bibinfo{volume}{47}, \bibinfo{pages}{319--323}.
\newblock \DOIprefix\doi{10.1016/0020-0190(93)90079-O}.
\bibitem[{Friedman(1937)}]{friedman1937}
\bibinfo{author}{Friedman, M.}, \bibinfo{year}{1937}.
\newblock \bibinfo{title}{The use of ranks to avoid the assumption of normality
  implicit in the analysis of variance}.
\newblock \bibinfo{journal}{Journal of the American Statistical Association}
  \bibinfo{volume}{32}, \bibinfo{pages}{675--701}.
\bibitem[{Gagolewski(2022)}]{clustering-benchmarks}
\bibinfo{author}{Gagolewski, M.}, \bibinfo{year}{2022}.
\newblock \bibinfo{title}{A framework for benchmarking clustering algorithms}.
\newblock \bibinfo{journal}{SoftwareX} \bibinfo{volume}{20},
  \bibinfo{pages}{101270}.
\newblock \DOIprefix\doi{10.1016/j.softx.2022.101270}.
\bibitem[{Gagolewski et~al.(2021)Gagolewski, Bartoszuk and Cena}]{cvi}
\bibinfo{author}{Gagolewski, M.}, \bibinfo{author}{Bartoszuk, M.},
  \bibinfo{author}{Cena, A.}, \bibinfo{year}{2021}.
\newblock \bibinfo{title}{Are cluster validity measures (in)valid?}
\newblock \bibinfo{journal}{Information Sciences} \bibinfo{volume}{581},
  \bibinfo{pages}{620--636}.
\newblock \DOIprefix\doi{10.1016/j.ins.2021.10.004}.
\bibitem[{Holland et~al.(1983)Holland, Laskey and Leinhardt}]{holland-sbm}
\bibinfo{author}{Holland, P.W.}, \bibinfo{author}{Laskey, K.B.},
  \bibinfo{author}{Leinhardt, S.}, \bibinfo{year}{1983}.
\newblock \bibinfo{title}{Stochastic blockmodels: First steps}.
\newblock \bibinfo{journal}{Social Networks} \bibinfo{volume}{5},
  \bibinfo{pages}{109--137}.
\newblock \DOIprefix\doi{10.1016/0378-8733(83)90021-7}.
\bibitem[{Hu et~al.(2021)Hu, Ma, Zhan, Zhou, Liu, Zhao and Zhang}]{Hu2021}
\bibinfo{author}{Hu, F.}, \bibinfo{author}{Ma, L.}, \bibinfo{author}{Zhan,
  X.X.}, \bibinfo{author}{Zhou, Y.}, \bibinfo{author}{Liu, C.},
  \bibinfo{author}{Zhao, H.}, \bibinfo{author}{Zhang, Z.K.},
  \bibinfo{year}{2021}.
\newblock \bibinfo{title}{The aging effect in evolving scientific citation
  networks}.
\newblock \bibinfo{journal}{Scientometrics} \bibinfo{volume}{126},
  \bibinfo{pages}{4297--4309}.
\newblock \DOIprefix\doi{10.1007/s11192-021-03929-8}.
\bibitem[{Hu et~al.(2020)Hu, Fey, Zitnik, Dong, Ren, Liu, Catasta and
  Leskovec}]{ogbn-arxiv}
\bibinfo{author}{Hu, W.}, \bibinfo{author}{Fey, M.}, \bibinfo{author}{Zitnik,
  M.}, \bibinfo{author}{Dong, Y.}, \bibinfo{author}{Ren, H.},
  \bibinfo{author}{Liu, B.}, \bibinfo{author}{Catasta, M.},
  \bibinfo{author}{Leskovec, J.}, \bibinfo{year}{2020}.
\newblock \bibinfo{title}{{Open Graph Benchmark}: {D}atasets for machine
  learning on graphs}.
\newblock \bibinfo{journal}{Advances in Neural Information Processing Systems}
  \bibinfo{volume}{33}, \bibinfo{pages}{22118--22133}.
\bibitem[{Jaeger and Banks(2023)}]{JaegerBanks2023:clustanalrev}
\bibinfo{author}{Jaeger, A.}, \bibinfo{author}{Banks, D.},
  \bibinfo{year}{2023}.
\newblock \bibinfo{title}{Cluster analysis: {A} modern statistical review}.
\newblock \bibinfo{journal}{Wiley Interdisciplinary Reviews: Computational
  Statistics} \bibinfo{volume}{15}, \bibinfo{pages}{e1597}.
\newblock \DOIprefix\doi{10.1002/wics.1597}.
\bibitem[{Karrer and Newman(2009)}]{karrernewman2009}
\bibinfo{author}{Karrer, B.}, \bibinfo{author}{Newman, M.E.J.},
  \bibinfo{year}{2009}.
\newblock \bibinfo{title}{Random graph models for directed acyclic networks}.
\newblock \bibinfo{journal}{Physical Review E} \bibinfo{volume}{80},
  \bibinfo{pages}{046110}.
\newblock \DOIprefix\doi{10.1103/PhysRevE.80.046110}.
\bibitem[{Karrer and Newman(2011)}]{karrer2011dcsbm}
\bibinfo{author}{Karrer, B.}, \bibinfo{author}{Newman, M.E.J.},
  \bibinfo{year}{2011}.
\newblock \bibinfo{title}{Stochastic blockmodels with a growing number of
  classes}.
\newblock \bibinfo{journal}{Physical Review E} \bibinfo{volume}{83},
  \bibinfo{pages}{016107}.
\newblock \DOIprefix\doi{10.1103/PhysRevE.83.016107}.
\bibitem[{Lancichinetti et~al.(2008)Lancichinetti, Fortunato and
  Radicchi}]{lancichinetti-lfr}
\bibinfo{author}{Lancichinetti, A.}, \bibinfo{author}{Fortunato, S.},
  \bibinfo{author}{Radicchi, F.}, \bibinfo{year}{2008}.
\newblock \bibinfo{title}{Benchmark graphs for testing community detection
  algorithms}.
\newblock \bibinfo{journal}{Physical Review E} \bibinfo{volume}{78}.
\newblock \DOIprefix\doi{10.1103/physreve.78.046110}.
\bibitem[{Lee and Wilkinson(2019)}]{lee-sbm}
\bibinfo{author}{Lee, C.}, \bibinfo{author}{Wilkinson, D.},
  \bibinfo{year}{2019}.
\newblock \bibinfo{title}{A review of {S}tochastic {B}lock {M}odels and
  extensions for graph clustering}.
\newblock \bibinfo{journal}{Applied Network Science} \bibinfo{volume}{4}.
\newblock \DOIprefix\doi{10.1007/s41109-019-0232-2}.
\bibitem[{Legramanti et~al.(2022)Legramanti, Rigon and
  Durante}]{Legramanti2022exogenous}
\bibinfo{author}{Legramanti, S.}, \bibinfo{author}{Rigon, T.},
  \bibinfo{author}{Durante, D.}, \bibinfo{year}{2022}.
\newblock \bibinfo{title}{Bayesian testing for exogenous partition structures
  in {S}tochastic {B}lock {M}odels}.
\newblock \bibinfo{journal}{Sankhya A} \bibinfo{volume}{84},
  \bibinfo{pages}{108--126}.
\newblock \DOIprefix\doi{10.1007/s13171-020-00231-2}.
\bibitem[{Leskovec and Krevl(2014)}]{snapnets}
\bibinfo{author}{Leskovec, J.}, \bibinfo{author}{Krevl, A.},
  \bibinfo{year}{2014}.
\newblock \bibinfo{title}{{SNAP Datasets}: {Stanford} large network dataset
  collection}.
\newblock \bibinfo{howpublished}{\url{http://snap.stanford.edu/data}}.
\bibitem[{Li et~al.(2020)Li, Yu, Li, Zhang, Zhao, Rong, Cheng and Huang}]{gvae}
\bibinfo{author}{Li, J.}, \bibinfo{author}{Yu, J.}, \bibinfo{author}{Li, J.},
  \bibinfo{author}{Zhang, H.}, \bibinfo{author}{Zhao, K.},
  \bibinfo{author}{Rong, Y.}, \bibinfo{author}{Cheng, H.},
  \bibinfo{author}{Huang, J.}, \bibinfo{year}{2020}.
\newblock \bibinfo{title}{{D}irichlet graph variational autoencoder}, in:
  \bibinfo{editor}{Larochelle, H.}, \bibinfo{editor}{Ranzato, M.},
  \bibinfo{editor}{Hadsell, R.}, \bibinfo{editor}{Balcan, M.},
  \bibinfo{editor}{Lin, H.} (Eds.), \bibinfo{booktitle}{Advances in Neural
  Information Processing Systems}, pp. \bibinfo{pages}{5274--5283}.
\bibitem[{Metzler and Miettinen(2019)}]{metzler2019}
\bibinfo{author}{Metzler, S.}, \bibinfo{author}{Miettinen, P.},
  \bibinfo{year}{2019}.
\newblock \bibinfo{title}{Hygen: {G}enerating random graphs with hyperbolic
  communities}.
\newblock \bibinfo{journal}{Applied Network Science} \bibinfo{volume}{4}.
\newblock \DOIprefix\doi{10.1007/s41109-019-0166-8}.
\bibitem[{Moore(2017)}]{cristopher_moore_cd59a506}
\bibinfo{author}{Moore, C.}, \bibinfo{year}{2017}.
\newblock \bibinfo{title}{The computer science and physics of community
  detection: Landscapes, phase transitions, and hardness}.
\newblock \bibinfo{journal}{Bulletin of the EATCS} \bibinfo{volume}{121}.
\bibitem[{Nanumyan et~al.(2020)Nanumyan, Gote and
  Schweitzer}]{vahan_nanumyan_c472afff}
\bibinfo{author}{Nanumyan, V.}, \bibinfo{author}{Gote, C.},
  \bibinfo{author}{Schweitzer, F.}, \bibinfo{year}{2020}.
\newblock \bibinfo{title}{Multilayer network approach to modeling authorship
  influence on citation dynamics in physics journals}.
\newblock \bibinfo{journal}{Physical Review E} \bibinfo{volume}{102}.
\newblock \DOIprefix\doi{10.1103/physreve.102.032303}.
\bibitem[{Nath et~al.(2021)Nath, Shanmugam and Varadaranjan}]{nath2021}
\bibinfo{author}{Nath, K.}, \bibinfo{author}{Shanmugam, R.},
  \bibinfo{author}{Varadaranjan, V.}, \bibinfo{year}{2021}.
\newblock \bibinfo{title}{{ma-CODE}: {A} multi-phase approach on community
  detection in evolving networks}.
\newblock \bibinfo{journal}{Information Sciences} \bibinfo{volume}{569},
  \bibinfo{pages}{326--343}.
\newblock \DOIprefix\doi{10.1016/j.ins.2021.02.068}.
\bibitem[{Newman(2018)}]{newman-networks}
\bibinfo{author}{Newman, M.}, \bibinfo{year}{2018}.
\newblock \bibinfo{title}{Networks}.
\newblock \bibinfo{publisher}{Oxford University Press}.
\newblock \DOIprefix\doi{10.1093/oso/9780198805090.001.0001}.
\bibitem[{Newman(2009)}]{newman2009}
\bibinfo{author}{Newman, M.E.J.}, \bibinfo{year}{2009}.
\newblock \bibinfo{title}{The first-mover advantage in scientific publication}.
\newblock \bibinfo{journal}{EPL (Europhysics Letters)} \bibinfo{volume}{86},
  \bibinfo{pages}{68001--68001}.
\newblock \DOIprefix\doi{10.1209/0295-5075/86/68001}.
\bibitem[{Price(1965)}]{deSollaPrice1965}
\bibinfo{author}{Price, D.}, \bibinfo{year}{1965}.
\newblock \bibinfo{title}{Networks of scientific papers}.
\newblock \bibinfo{journal}{Science} \bibinfo{volume}{149},
  \bibinfo{pages}{510--515}.
\newblock \DOIprefix\doi{10.1126/science.149.3683.510}.
\bibitem[{Rosvall et~al.(2009)Rosvall, Axelsson and Bergstrom}]{Rosvall2009}
\bibinfo{author}{Rosvall, M.}, \bibinfo{author}{Axelsson, D.},
  \bibinfo{author}{Bergstrom, C.T.}, \bibinfo{year}{2009}.
\newblock \bibinfo{title}{The map equation}.
\newblock \bibinfo{journal}{The European Physical Journal Special Topics}
  \bibinfo{volume}{178}, \bibinfo{pages}{13--23}.
\newblock \DOIprefix\doi{10.1140/epjst/e2010-01179-1}.
\bibitem[{Sen et~al.(2008)Sen, Namata, Bilgic, Getoor, Gallagher and
  Eliassi-Rad}]{cora-dataset}
\bibinfo{author}{Sen, P.}, \bibinfo{author}{Namata, G.M.},
  \bibinfo{author}{Bilgic, M.}, \bibinfo{author}{Getoor, L.},
  \bibinfo{author}{Gallagher, B.}, \bibinfo{author}{Eliassi-Rad, T.},
  \bibinfo{year}{2008}.
\newblock \bibinfo{title}{Collective classification in network data}.
\newblock \bibinfo{journal}{AI Magazine} \bibinfo{volume}{29},
  \bibinfo{pages}{93--106}.
\bibitem[{Siudem et~al.(2020)Siudem, Żogała Siudem, Cena and
  Gagolewski}]{3dsi-pnas}
\bibinfo{author}{Siudem, G.}, \bibinfo{author}{Żogała Siudem, B.},
  \bibinfo{author}{Cena, A.}, \bibinfo{author}{Gagolewski, M.},
  \bibinfo{year}{2020}.
\newblock \bibinfo{title}{Three dimensions of scientific impact}.
\newblock \bibinfo{journal}{Proceedings of the National Academy of Sciences of
  the United States of America (PNAS)} \bibinfo{volume}{117},
  \bibinfo{pages}{13896--13900}.
\newblock \DOIprefix\doi{10.1073/pnas.2001064117}.
\bibitem[{Speidel et~al.(2015)Speidel, Takaguchi and Masuda}]{speidel2015}
\bibinfo{author}{Speidel, L.}, \bibinfo{author}{Takaguchi, T.},
  \bibinfo{author}{Masuda, N.}, \bibinfo{year}{2015}.
\newblock \bibinfo{title}{Community detection in directed acyclic graphs}.
\newblock \bibinfo{journal}{The European Physical Journal B}
  \bibinfo{volume}{88}.
\newblock \DOIprefix\doi{10.1140/epjb/e2015-60226-y}.
\bibitem[{Sun et~al.(2017)Sun, Ajwani, Nicholson, Sala and
  Parthasarathy}]{Sun2017}
\bibinfo{author}{Sun, J.}, \bibinfo{author}{Ajwani, D.},
  \bibinfo{author}{Nicholson, P.K.}, \bibinfo{author}{Sala, A.},
  \bibinfo{author}{Parthasarathy, S.}, \bibinfo{year}{2017}.
\newblock \bibinfo{title}{Breaking cycles in noisy hierarchies}, in:
  \bibinfo{booktitle}{Proceedings of the 2017 ACM on Web Science Conference},
  \bibinfo{publisher}{Association for Computing Machinery},
  \bibinfo{address}{New York, NY, USA}. p. \bibinfo{pages}{151–160}.
\newblock \DOIprefix\doi{10.1145/3091478.3091495}.
\bibitem[{Tang et~al.(2008)Tang, Zhang, Yao, Li, Zhang and Su}]{dblp-dataset}
\bibinfo{author}{Tang, J.}, \bibinfo{author}{Zhang, J.}, \bibinfo{author}{Yao,
  L.}, \bibinfo{author}{Li, J.}, \bibinfo{author}{Zhang, L.},
  \bibinfo{author}{Su, Z.}, \bibinfo{year}{2008}.
\newblock \bibinfo{title}{Arnetminer: Extraction and mining of academic social
  networks}, in: \bibinfo{booktitle}{KDD'08}, pp. \bibinfo{pages}{990--998}.
\bibitem[{Traag et~al.(2019)Traag, Waltman and van Eck}]{traag-leiden}
\bibinfo{author}{Traag, V.}, \bibinfo{author}{Waltman, L.},
  \bibinfo{author}{van Eck, N.J.}, \bibinfo{year}{2019}.
\newblock \bibinfo{title}{From {L}ouvain to {L}eiden: {G}uaranteeing
  well-connected communities}.
\newblock \bibinfo{journal}{Scientific Reports} \bibinfo{volume}{9},
  \bibinfo{pages}{5233}.
\newblock \DOIprefix\doi{10.1038/s41598-019-41695-z}.
\bibitem[{Ullmann et~al.(2022)Ullmann, Hennig and
  Boulesteix}]{UllmanETAL2022:wiresvalidationclust}
\bibinfo{author}{Ullmann, T.}, \bibinfo{author}{Hennig, C.},
  \bibinfo{author}{Boulesteix, A.L.}, \bibinfo{year}{2022}.
\newblock \bibinfo{title}{Validation of cluster analysis results on validation
  data: {A} systematic framework}.
\newblock \bibinfo{journal}{Wiley Interdisciplinary Reviews: Data Mining and
  Knowledge Discovery} \bibinfo{volume}{12}, \bibinfo{pages}{e1444}.
\newblock \DOIprefix\doi{10.1002/widm.1444}.
\bibitem[{{van Mechelen} et~al.(2023){van Mechelen}, Boulesteix, Dangl
  et~al.}]{VanMechelenETAL2023:whitepaperclustbench}
\bibinfo{author}{{van Mechelen}, I.}, \bibinfo{author}{Boulesteix, A.L.},
  \bibinfo{author}{Dangl, R.}, et~al., \bibinfo{year}{2023}.
\newblock \bibinfo{title}{A white paper on good research practices in
  benchmarking: {T}he case of cluster analysis}.
\newblock \bibinfo{journal}{Wiley Interdisciplinary Reviews: Data Mining and
  Knowledge Discovery} \bibinfo{volume}{13}, \bibinfo{pages}{e1511}.
\newblock \DOIprefix\doi{10.1002/widm.1511}.
\bibitem[{Wang et~al.(2013)Wang, Song and Barab{\'a}si}]{wang2013}
\bibinfo{author}{Wang, D.}, \bibinfo{author}{Song, C.},
  \bibinfo{author}{Barab{\'a}si, A.L.}, \bibinfo{year}{2013}.
\newblock \bibinfo{title}{Quantifying long-term scientific impact}.
\newblock \bibinfo{journal}{Science} \bibinfo{volume}{342},
  \bibinfo{pages}{127--132}.
\bibitem[{Wiliński et~al.(2019)Wiliński, Mazzarisi, Tantari and
  Lillo}]{wilinski2019}
\bibinfo{author}{Wiliński, M.}, \bibinfo{author}{Mazzarisi, P.},
  \bibinfo{author}{Tantari, D.}, \bibinfo{author}{Lillo, F.},
  \bibinfo{year}{2019}.
\newblock \bibinfo{title}{Detectability of macroscopic structures in directed
  asymmetric {S}tochastic {B}lock {M}odel}.
\newblock \bibinfo{journal}{Physical Review E} \bibinfo{volume}{99}.
\newblock \DOIprefix\doi{10.1103/physreve.99.042310}.
\bibitem[{Zhu et~al.(2020)Zhu, Chen and Zeng}]{zhu2020}
\bibinfo{author}{Zhu, J.}, \bibinfo{author}{Chen, B.}, \bibinfo{author}{Zeng,
  Y.}, \bibinfo{year}{2020}.
\newblock \bibinfo{title}{Community detection based on modularity and
  k-plexes}.
\newblock \bibinfo{journal}{Information Sciences} \bibinfo{volume}{513},
  \bibinfo{pages}{127--142}.
\newblock \DOIprefix\doi{10.1016/j.ins.2019.10.076}.

\end{thebibliography}



\end{document}
