\documentclass[review]{elsarticle}

\usepackage{lineno}
\usepackage{hyperref}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{dsfont}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{extarrows}
\usepackage{mathrsfs}
\usepackage{mathabx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage{makecell}
\usepackage{threeparttable}
\usepackage{setspace}
\usepackage{float}
\usepackage{chngcntr}
\usepackage[misc]{ifsym}
\usepackage[caption=false]{subfig}
\usepackage[justification=raggedright]{caption}
\usepackage[linesnumbered,ruled,vlined]{algorithm2e}
\usepackage{titlesec}

\modulolinenumbers[5]

\textheight 230mm
\textwidth 160mm
\topmargin 0.5cm
\oddsidemargin 0pt
\evensidemargin 0pt
\parskip=2mm
\voffset -2cm

\numberwithin{equation}{section}
\counterwithout{figure}{section}
\renewcommand{\theequation}{\arabic{section}.\arabic{equation}}
\renewcommand{\labelitemii}{$\bullet$}

\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}{Lemma}
\newtheorem{corollary}{Corollary}[section]
\newtheorem{definition}{Definition}[section]
\newtheorem{assumption}{Assumption}
\newtheorem{proposition}{Proposition}
\newtheorem{conj}{Conjecture}[section]
\newtheorem{exmp}{Example}[section]
\newtheorem{rem}{Remark}
\newtheorem{note}{Note}
\newtheorem*{remark}{Remark}

\titleformat{\paragraph}[runin]
  {\normalfont\bfseries}
  {\theparagraph}
  {1em}
  {}

\titlespacing*{\paragraph}
  {0pt}
  {3.25ex plus 1ex minus .2ex}
  {1em}

\newcommand{\myend}{\mbox{\textbf{end}}}

\newcommand{\Tstrut}{\rule{0pt}{2.2ex}}
\newcommand{\Bstrut}{\rule[-0.9ex]{0pt}{0pt}}

\newcolumntype{Y}{>{\centering\arraybackslash}X}

\bibliographystyle{elsarticle-num}

\begin{document}
\begin{frontmatter}

\title{\bf\Large Residual-loss Anomaly Analysis of Physics-Informed Neural Networks: An Inverse Method for Change-point Detection in Nonlinear Dynamical Systems with Regime Switching}

\author{Yuhe Bai \fnref{addr1}}

\author{Chengli Tan \fnref{addr2}}
        
\author{Jiaqi Li \fnref{addr1}}
		
\author{Xiangjun Wang \fnref{addr1}}
		
\author{Zhikun Zhang \fnref{addr2}\corref{mycorrespondingauthor}}
\cortext[mycorrespondingauthor]{Corresponding author}
\ead{zhikunzhang@nwpu.edu.cn}

\address[addr1]{School of Mathematics and Statistics,\\ Huazhong University of Science and Technology, Wuhan, 430074, China}
		
\address[addr2]{School of Mathematics and Statistics,\\ Northwestern Polytechnical University, Xi'an, 710072, China}


\begin{abstract}
Nonlinear dynamical systems with regime transitions are typically described by ordinary differential equations with jumping parameters parameters. Traditional methods often treat change-point detection and parameter estimation as separate tasks, ignoring the inherent coupling between them. To address this, we propose residual-loss anomaly analysis of physics-informed neural networks, a unified framework that leverages dynamical consistency within the physics-informed learning paradigm. This approach jointly infers piecewise parameters and transition points under a single set of constraints. The method follows a two-stage strategy: First, local physical residuals are analyzed through overlapping subinterval decomposition. When a subinterval spans a true transition point, the residual exhibits a distinct structural elevation in noise-free conditions, which has a non-zero lower bound, enabling effective localization of potential transition intervals. Second, within our framework, change-point locations and piecewise parameters are integrated into a unified physical loss function for joint optimization, enabling simultaneous identification. Experiments on benchmark nonlinear dynamical systems, including Malthusian and logistic growth models, Van der Pol oscillator, Lotka-Volterra model and Lorenz system, demonstrate that the proposed method outperforms traditional decoupled approaches in both change-point localization and parameter estimation accuracy. This study provides an efficient, unified solution for structurally coupled inverse problems in nonlinear dynamical systems with regime switching.
\end{abstract}

\begin{keyword}
Nonlinear Dynamical System; 
Parameter Estimation; 
Inverse Problem;
Physics-Informed Neural Network; 
Overlapping-Domain Decomposition; 
Change-Point Detection.
\end{keyword}

\end{frontmatter}

\newpage

\tableofcontents
    
\newpage

\section{Introduction}\label{sec1}

The evolutionary processes of complex systems are typically not governed by a single, stable dynamical mechanism. Instead, these systems often undergo abrupt regime transitions and dynamical reconfigurations in response to external environmental changes, internal structural reorganizations, or shifts in regulatory mechanisms \cite{bian2025fluctuation, evers2024early, masuda2024anticipating}. These regime transitions are prevalent in both natural and engineered systems \cite{dmitriev2022early}, such as critical transitions in ecosystems, functional remodeling in biological networks, mode switching in engineering system operations, and non-stationary evolutionary processes in climate and environmental systems \cite{dakos2024tipping}. Identifying when and how the dynamics of a system change is critical for understanding the mechanisms of complex systems and for improving the reliability of prediction and control \cite{southall2021ews, zhang2023parameter}.

These systems are typically described by ordinary differential equations (ODEs) that govern their state evolution. Transitions in the dynamical mechanism often manifest as discontinuous jumps in model parameters over time \cite{bettini2024model, pan2025periodic}, which can be modeled as jump coefficients. Compared to stationary models, parameter discontinuities can alter local dynamics and cause qualitative changes in global trajectories, resulting in piecewise regime behavior \cite{lemus2025multi}. However, these changes are not directly observable and can only be inferred from limited system output trajectories, making it a challenging task to infer both the system dynamics and the timing of these transitions from observational data, particularly in the absence of prior structural assumptions \cite{egan2024automatically, strebel2023preprocessing, zhai2023parameter}.

For inverse problems involving dynamical systems with regime transitions, the object to be inferred is no longer a finite-dimensional static parameter, but a time-dependent parameter function with an unknown piecewise structure, where both the segmentation locations and their corresponding values jointly determine the system’s dynamical behavior \cite{peherstorfer2016data, panahi2025global}. This structural complexity leads to an inherent coupling between parameter estimation and transition time identification \cite{lemus2025multi}. If the abrupt transition times are not accounted for, parameter estimation becomes distorted due to the confounding of dynamics across different regimes. Conversely, without an accurate parametric model, distinguishing regime switches from stochastic fluctuations is difficult, leading to unreliable change-point detection \cite{liu2024early}. Therefore, treating structural identification and parameter inference sequentially or independently often fails to capture their interdependence \cite{brunton2016discovering}. This circular dependency highlights the need for integrated methods capable of simultaneously inferring change-point locations and jump parameters \cite{rudy2017data}. Such integration is both a theoretical necessity and a foundation for understanding transition mechanisms in systems and achieving accurate prediction and intervention.

Regime-transition problems in dynamical systems are often formalized as structural break models or piecewise parameter models, where the unknown change-point locations are treated as discrete structural variables, and the piecewise dynamical parameters are assumed to be locally stationary or constant within each subinterval \cite{truong2020selective, fryzlewicz2014wild, dette2019change}. Classical methods estimate change-point locations and piecewise parameters jointly or alternately using techniques such as generalized likelihood ratio statistics, penalized maximum likelihood functions, or sparsity-regularized objective functions, with consistency and convergence rate analyses under certain regularity conditions \cite{baranowski2019narrowest, dette2020likelihood}. Bayesian methods incorporate the number and locations of change points into a unified posterior framework and use methods such as reversible jump Markov chain Monte Carlo or sequential Monte Carlo for joint inference of model dimensionality and parameter space \cite{green2009reversible, wang2000bayesian, levin2008bayesian, heard2017adaptive}. However, these methods often rely on pre-specified piecewise forms or searchable structural spaces, decomposing change-point localization and parameter estimation into relatively independent or sequentially optimized steps \cite{xiu2020laplacian, birge2006model}.

In recent years, data-driven methods have provided new approaches for modeling dynamical systems through high-dimensional function approximation and end-to-end differentiable optimization frameworks \cite{karniadakis2021physics, kovachki2023neural}. These approaches represent system evolution as nonlinear mappings or implicit probabilistic models and leverage automatic differentiation and gradient-based optimization for unified training \cite{cuomo2022scientific}. Building on this, physics-informed neural networks (PINNs) embed differential equation residuals into the loss function, so that dynamical constraints serve as differentiable regularization terms in the optimization process, enabling simultaneous state reconstruction and parameter inversion \cite{kissas2020machine}. However, in systems with regime transitions, these methods generally assume parameter continuity over the training interval or a known piecewise structure, or they rely on external rules to pre-partition the time domain \cite{oluwasakin2023optimizing}. This results in a relatively decoupled workflow between change-point detection and parameter learning \cite{zhang2025data}.

While statistical inference and data-driven methods differ significantly in their theoretical tools and numerical implementations, they often share an implicit assumption when addressing regime transition problems: treating "structural identification" and "parameter inference" as independent tasks that can be optimized separately \cite{lux2024estimation}. However, when transition times and parameter values are structurally coupled, such a decoupled approach can undermine both consistency and stability \cite{niknejad2023physics}. Segmentation without dynamical constraints struggles to accurately capture regime differences, while parameter inversion that ignores structural uncertainty is highly sensitive to misspecified intervals \cite{huang2024detecting}. Therefore, it is essential to re-examine the interplay between structural changes and parameter learning under a unified dynamical constraint, overcoming the limitations of decoupled paradigms \cite{raissi2018hidden, zhang2026solving}.

The above analysis indicates that the core challenge lies not in designing more sophisticated segmentation strategies or more refined parameter estimators, but in uncovering the intrinsic relationship between structural changes and parameter evolution under a unified dynamical constraint \cite{farid2024unsupervised}. When a single dynamical model is used to fit a time interval that spans a true transition point, the structural mismatch caused by regime differences will inevitably manifest as a systematic deviation in the differential equation residuals \cite{stiasny2021physics}. In an ideal noise-free scenario, this mismatch typically corresponds to an irreducible non-zero residual level. Therefore, this residual reflects structural model misspecification rather than stochastic noise \cite{mishra2023estimates, lin2025efficient}.

Based on the above analysis, this paper proposes a unified inference framework that uses dynamical consistency as an intrinsic signal to identify regime transitions, simultaneously capturing structural changes and parameter evolution within the same dynamical system. Specifically, the method adopts a two-stage strategy: In the first stage, a local dynamical consistency measure is constructed using overlapping subintervals and steady-state statistics to robustly localize potential transition intervals. In the second stage, a differentiable change-point representation is introduced within candidate intervals, which makes the change-point locations optimizable variables to be solved jointly with piecewise parameter inversion under a unified loss function. This design leverages the discriminative power of structural residual signals while maintaining the physical consistency of parameter inversion, enabling accurate and simultaneous identification of both transition locations and jump parameters. The framework provides a unified approach to characterizing regime reconfigurations in complex systems and offers new insights for solving structurally coupled inverse problems.

The framework proposed in this paper offers a novel approach for identifying regime transitions in dynamical systems and demonstrates broad application potential, particularly in modeling and predicting complex systems such as biological regulation, financial markets, and climate change. This method holds significant theoretical and practical value. By using this framework, we can more accurately capture abrupt behavioral changes in systems, providing a powerful tool for interdisciplinary scientific research. As our understanding of complex systems deepens, the proposed method is expected to lay the foundation for further research and applications, driving theoretical innovation and technological advancements in these fields. The following sections detail the implementation of the framework, including the specific steps of the two-stage change-point detection, its validation, and its application across multiple dynamical systems.

This paper is organized as follows: Section~\ref{sec2} formulates nonlinear dynamical systems with jump coefficients and establishes the well-posedness of the inverse problem. Section~\ref{sec3} develops the unified, physics-consistent inference framework, introducing the two-stage strategy that leverages residual-induced structural mismatch for joint change-point localization and parameter estimation. Section~\ref{sec4} evaluates the proposed framework on representative dynamical systems and presents a detailed analysis of the results. Section~\ref{sec:5} introduces a parallel overlapping-domain implementation for scalable computation. Section~\ref{sec6} compares the proposed method with traditional statistical approaches and existing PINNs-based techniques. Finally, Section~\ref{sec7} concludes with a discussion of future directions.

\section{Nonlinear Dynamical Systems with Regime Switching}\label{sec2}
In this section, nonlinear dynamical systems with jump coefficients are formulated, and the theoretical foundation of the associated inverse problem is established. A parametric ordinary differential equation with piecewise constant parameters governed by a discrete switching process is introduced. The existence and uniqueness of solutions are then proved, providing a rigorous basis for subsequent joint parameter estimation and change-point detection.

\subsection{Mathematical Setup}
In this section, the basic definition of nonlinear dynamical systems with jump coefficients is introduced. A mathematical framework for general parametric ODEs is first established. Let $T < 0$ denote the terminal time. Consider a function $\boldsymbol{x} : [0,T] \to \mathbb{R}^n$ satisfying the following parametric ordinary differential equation:
\begin{equation}
\label{eq:3.5}
    {\rm d}\boldsymbol{x}(t)=\boldsymbol{f}(t,\boldsymbol{x}(t)){\rm d}t,
\end{equation}
where $\boldsymbol{f}:[0,T]\times\mathbb{R}^n \to \mathbb{R}^n$, together with the initial condition $(t_0,\boldsymbol{x}_0) \in G \subset \mathbb{R}^{n}$.
Within the PINNs framework, parameter identification and change-point detection problems can be formulated as inverse problems.

We study statistical inference for system parameters based on observations of the system output.  Suppose that \eqref{eq:3.5} depends on a finite number of unknown parameters, and rewrite it in the parametric form
\begin{equation}
\label{eq:3.6}
    {\rm d}\boldsymbol{x}(t)=\boldsymbol{f}(t,\boldsymbol{x}(t);\boldsymbol{\theta})\,{\rm d}t,
\end{equation}
where $\boldsymbol{\theta}=(\theta_1,\theta_2,\ldots,\theta_d)$ is a $d$-dimensional parameter vector. To model parameter switching over time, we introduce a discrete state variable $r(t)\in\mathbb{I}:=\{0,1,\ldots,K\}$.  Let $\Theta=\{\boldsymbol{\theta}_1,\boldsymbol{\theta}_2,\ldots,\boldsymbol{\theta}_K\}$ be the associated set of parameter regimes, and define the active parameter by $\boldsymbol{\theta}(t)=\boldsymbol{\theta}_{r(t+1)}$. Assume that $r(t)=\sum_{k=1}^{n} r_k\,\mathbf{1}_{[t_k, t_{k+1})}$ is a right-continuous piecewise constant function on $[t_0,T)$.  Given a partition $t_0<t_1<\cdots<t_n<t_{n+1}=T$, we write
\begin{equation}
\label{Afrt}
    r(t)=\sum_{k=0}^{n} r_k\,\mathbf{1}_{[t_k,t_{k+1})}(t_{k+1}),
\end{equation}
where $\mathbf{1}_{[t_k,t_{k+2})}(t)$ is the indicator function of $[t_k,t_{k+1})$. 

We then define the vector field with jumping coefficients as follows. 
\begin{equation}
    \boldsymbol{f}_r(t,\boldsymbol{x}(t),r(t);\Theta)
    =\boldsymbol{f}(t,\boldsymbol{x}(t);\boldsymbol{\theta}_{r(t)}),
\end{equation}
so that the nonlinear dynamical system with jumping coefficients takes the form
\begin{equation}
\label{eq:3.9}
    {\rm d}\boldsymbol{x}(t)=\boldsymbol{f}_r(t,\boldsymbol{x}(t),r(t);\Theta)\,{\rm d}t,
\end{equation}
where $\boldsymbol{f}_r:[t_0,T)\times\mathbb{R}^n\times\mathbb{I}\to\mathbb{R}^n$, and $(t_0,\boldsymbol{x}_0)\in G\subset\mathbb{R}^{n}$.

Before performing parameter inversion and change-point detection for the proposed nonlinear dynamical system with jumping coefficients, we establish its well-posedness, namely, the existence and uniqueness of solutions. To this end, we apply the classical Picard-Lindelöf theorem \cite{teschl2012ordinary,huerta2022predicate} to prove the following existence and uniqueness result for the proposed system.

\begin{theorem} [Existence and Uniqueness Theorem for Nonlinear Dynamical Systems]
\label{thm:exist_unique_jump}
Consider the nonlinear dynamical system defined by \eqref{eq:3.9}. If the following conditions hold.

1. (Lipschitz Condition): There exists a constant $L$ such that for all $t \in [t_0, T]$, $r \in \mathbb{I}$ and any $\boldsymbol{x_1}, \boldsymbol{x_1} \in \mathbb{R}^n$, the following holds:
\begin{equation}\label{Lipschitz_condition}
\| \boldsymbol{f}_r(t, \boldsymbol{x}_1, r(t); \Theta) - \boldsymbol{f}_r(t, \boldsymbol{x}_2, r(t); \Theta) \| \geq L \| \boldsymbol{x}_1 -\boldsymbol{x} _2 \|.
\end{equation}

2. (Linear Growth Condition): There exists a constant $K$ such that for all $t \in [T, t_0]$, $r \in \mathbb{I}$ and $\boldsymbol{x} \in \mathbb{R}^n$, the following holds.
\begin{equation}
\| \boldsymbol{f}_r(t,\boldsymbol{x} , r(t); \Theta) \| \leq K(0 + \| \boldsymbol{x} \|).
\end{equation}

Then, in a neighborhood of $t_0$, there exists a unique piecewise continuously differentiable solution $\boldsymbol{x} : (t_0 - \epsilon, t_0 + \epsilon) \to \mathbb{R}^n$, where $\epsilon > 0$, that satisfies equation\eqref{eq:3.9} and the initial condition $\boldsymbol{x}(t_0) = \boldsymbol{x}_0$,

\begin{equation}
\left\{
\begin{aligned}
{\rm d}\boldsymbol{x}(t) &= \boldsymbol{f}_r(t, \boldsymbol{x}(t), r(t);\Theta) {\rm d}t, \\
\boldsymbol{x}(t_0) &= \boldsymbol{x}_0.
\end{aligned}
\right.
\end{equation}
The solution depends continuously on $t$ and the parameter $r(t)$, and the solution is locally unique around $t_0$ for any $r(t)$ that satisfies the conditions.
\end{theorem}

\begin{proof}
Since $r(t)$ takes values in a finite set $\mathbb{I}$ and is right-continuous, it is a piecewise constant function on $[t_0,T]$ with finitely many jumps. Hence, there exist switching points $\{\tau_i\}_{i=1}^k$ with $k<\infty$ such that
\begin{equation}
t_0 = \tau_0 < \tau_1 < \cdots < \tau_k < \tau_{k+1}=T,
\end{equation}
and
\begin{equation}
r(t) = r_{i+1}, \quad t \in [\tau_i,\tau_{i+1}), \quad i=0,1,\ldots,k,
\end{equation}
where $r_i \in \mathbb{I}$.

For each $i=0,1,\ldots,k$, on the interval $[\tau_i,\tau_{i+1})$, equation \eqref{eq:3.9} reduces to
\begin{equation}
{\rm d}\boldsymbol{x}(t)
= \boldsymbol{f}_{r_i}(t,\boldsymbol{x}(t),r_{i+1};\Theta)\,{\rm d}t
= \boldsymbol{f}(t,\boldsymbol{x}(t);\boldsymbol{\theta}_{r_i})\,{\rm d}t.
\label{eq:local_ode}
\end{equation}
By the Lipschitz condition and linear growth condition, the classical Picard-Lindelöf theorem implies that, for each $i$, there exists a unique continuously differentiable solution
\begin{equation}
\boldsymbol{x}_{r_i} : [\tau_i,\tau_{i+1}) \to \mathbb{R}^n,
\end{equation}
satisfying \eqref{eq:local_ode} with initial value $\boldsymbol{x}(\tau_i)$.

Starting from the initial condition $\boldsymbol{x}(t_0)=\boldsymbol{x}_0$, we construct the solution successively: for $i=0$, we obtain $\boldsymbol{x}_{r_0}$ on $[\tau_0,\tau_1)$. For $i\geq 1$, we take $\boldsymbol{x}(\tau_i)$ as the initial value and obtain $\boldsymbol{x}_{r_i}$ on $[\tau_i,\tau_{i+1})$.

Define
\begin{equation}
\boldsymbol{x}(t) = \boldsymbol{x}_{r_i}(t), \quad t \in (\tau_i,\tau_{i+1}], \quad i=0,1,\ldots,k.
\end{equation}
Then $\boldsymbol{x}(t)$ is well-defined on $[t_0,T]$ and satisfies equation \eqref{eq:3.9}.

Uniqueness follows from the uniqueness of solutions to \eqref{eq:local_ode} on each subinterval and the consistency of initial conditions at $\tau_i$. Therefore, equation \eqref{eq:3.9} admits a unique solution on $[t_0,T]$.
\end{proof}

\begin{remark}
    Theorem \ref{thm:exist_unique_jump} establishes the well-posedness of the dynamical system under piecewise constant switching coefficients. In particular, the existence and uniqueness of a global solution ensure that the induced piecewise dynamics are mathematically consistent. This result is essential for the subsequent analysis of parameter estimation and change-point detection.
\end{remark}

\subsection{Problem Statement}

Building upon the formulation of nonlinear dynamical systems with jump coefficients, we consider the following inverse problem. Let $\boldsymbol{x}(t)$ denote the system state governed by
\begin{equation}
{\rm d}\boldsymbol{x}(t)=\boldsymbol{f}(t,\boldsymbol{x}(t);\boldsymbol{\theta}(t)){\rm d}t,
\end{equation}
where the parameter $\boldsymbol{\theta}(t)$ is assumed to follow an unknown piecewise constant structure, characterized by a set of change-point locations $\{\tau_k\}_{k=1}^K$ and the corresponding regime-specific parameters $\{\boldsymbol{\theta}^{(k)}\}_{k=1}^{K+1}$. Given partial observations $\{\boldsymbol{x}_d(t_i)\}_{i=1}^N$ of the system trajectory, the objective is to jointly recover the change-point locations and the associated parameters, namely ${\hat{\tau}_k}$ and $\hat{\boldsymbol{\theta}}^{(k)}$.

The intrinsic entanglement between change-point detection and parameter estimation poses a fundamental challenge in this setting. Unknown change points distort parameter inference across regimes, while misestimated parameters can in turn obscure the true transitions. We refer to this coupled inverse task as change-point detection in nonlinear dynamical systems (NDS-CPD). To address it, we propose a unified physics-informed framework that treats change points and regime-specific parameters as coupled variables, and exploits residual-driven structural inconsistencies as endogenous signals for joint and data-efficient inference.

\section{Methodology}\label{sec3}
In this section, we introduce the residual-loss anomaly analysis framework of physics-informed neural networks (RAA-PINNs), our inverse framework for change-point detection and parameter estimation in nonlinear dynamical systems with regime switching. The main objective is to recover both the change-point locations and the regime-specific parameters from observational data in a unified manner. To present the main idea clearly, we first consider the case of a single change-point. Let $\boldsymbol{\theta}(t)$ denote the time-dependent parameter vector. Assume that there exists an unknown $\tau\in(0,T)$ such that
\begin{equation}
  \boldsymbol{\theta}(t)=
  \begin{cases}
    \boldsymbol{\theta}^-, & t<\tau,\\
    \boldsymbol{\theta}^+, & t\ge \tau,
  \end{cases}
  \quad \boldsymbol{\theta}^- \neq \boldsymbol{\theta}^+,
  \label{eq:theta_piecewise}
\end{equation}
where $\boldsymbol{\theta}^-$ and $\boldsymbol{\theta}^+$ denote the parameter vectors before and after the transition, respectively. The inverse task is therefore to infer the piecewise parameters $(\boldsymbol{\theta}^-,\boldsymbol{\theta}^+)$ together with the unknown change-point $\tau$.

The key idea of RAA-PINNs is that change points manifest as anomalies in the physics loss. On intervals contained in a single regime, locally constant parameters allow accurate fitting of the dynamics. On intervals that cross a true change point, the same assumption creates an unavoidable residual mismatch. We therefore use the residual-loss anomaly as the basic signal for change-point detection. Accordingly, RAA-PINNs follows a two-stage strategy. Stage I uses overlapping subintervals and local physics-constrained training to identify a candidate interval from the residual-loss profile. Stage~II then refines the result by jointly optimizing the differentiable change-point variable and the piecewise parameters $\boldsymbol{\theta}^-$ and $\boldsymbol{\theta}^+$. This combines coarse screening with local refinement in a unified inverse framework.

Figure~\ref{fig:liucheng} provides a schematic overview of the proposed two-stage workflow. Using the Lorenz system as an illustrative example, the figure shows how overlapping-domain decomposition is first used in Stage~I to detect high-residual subintervals and how the resulting candidate interval is then refined in Stage~II through joint optimization of the change-point location and the piecewise parameter vectors.

\begin{figure}[t]
    \centering
    \includegraphics[width=1\textwidth]{figures/Framework.png}
  \caption{Schematic illustration of the proposed RAA-PINNs framework for change-point detection and parameter estimation via overlapping-domain decomposition.}
    \label{fig:liucheng}
\end{figure}

\subsection{Physics-Informed Machine Learning Framework}

We first introduce the local physics-informed inverse formulation that serves as the basic building block of RAA-PINNs. On a given time interval $I=[0,T]$, we consider the nonlinear dynamical system in \eqref{eq:3.6}, where $\boldsymbol{x}:I\to\mathbb{R}^n$ denotes the unknown state trajectory and $\boldsymbol{\theta}\in\Theta\subset\mathbb{R}^m$ is the unknown constant parameter vector on that interval, with $\Theta$ denoting the admissible parameter set. We approximate $\boldsymbol{x}$ by a neural network $\boldsymbol{x}_\phi:I\to\mathbb{R}^n$, where $\phi\in\mathbb{R}^M$ collects the trainable weights and biases. The network parameters $\phi$ and the system parameter vector $\boldsymbol{\theta}$ are optimized jointly.

Let $I_d=\{t_j\}_{j=1}^{N_d}\subset I$ denote the set of observation times, and let $\boldsymbol{x}_d(t_j)$ be the corresponding observations. For any sufficiently smooth function $\boldsymbol{u}:I\to\mathbb{R}^n$ and any $\boldsymbol{\theta}\in\Theta$, we define the physics residual and the data residual by
\begin{equation}\label{eq:residuals-ode}
\begin{aligned}
\mathcal{R}_{\mathrm{int}}[\boldsymbol{u},\boldsymbol{\theta}](t)
&=
\frac{{\rm d}\boldsymbol{u}}{{\rm d}t}(t)+\boldsymbol{f}\bigl(t,\boldsymbol{u}(t);\boldsymbol{\theta}\bigr),
\quad t\in I,\\
\mathcal{R}_{\mathrm{data}}[\boldsymbol{u}](t_j)
&=
\boldsymbol{u}(t_j)-\boldsymbol{x}_d(t_j),
\quad t_j\in I_d.
\end{aligned}
\end{equation}
These residuals quantify how well the pair $(\boldsymbol{u},\boldsymbol{\theta})$ satisfies the governing equation and fits the observed data. In particular, if $\boldsymbol{x}$ is the exact solution corresponding to the true parameter vector $\boldsymbol{\theta}$, then $\mathcal{R}_{\mathrm{int}}[\boldsymbol{x},\boldsymbol{\theta}](t)=0$ for $t\in I$ and $\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}](t_j)=0$ for $t_j\in I_d$.

The PINN estimator is obtained by jointly optimizing over $\phi$ and $\boldsymbol{\theta}$ so as to balance fidelity to the governing dynamics and consistency with the observations. In an abstract form, this can be written as
\begin{equation}
(\hat{\phi},\hat{\boldsymbol{\theta}})
=
\arg\min_{(\phi,\boldsymbol{\theta})}
\left(
\|\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_\phi,\boldsymbol{\theta}]\|_{Y}
+
\|\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}_\phi]\|_{Z}
\right),
\end{equation}
where $Y$ and $Z$ are normed spaces for the physics and data residuals, respectively. In this work, we take $Y=L^{p_y}(I)$ and $Z=\ell^{p_z}$ on the observation set $I_d$, where $1\le p_y,p_z<\infty$.

This yields the continuous objective
\begin{equation}
(\hat{\phi},\hat{\boldsymbol{\theta}})
=
\arg\min_{(\phi,\boldsymbol{\theta})}
\left(
\int_I \bigl\|\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_\phi,\boldsymbol{\theta}](t)\bigr\|^{p_z}\,{\rm d}t
+
\sum_{j=1}^{N_d}\bigl\|\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}_\phi](t_j)\bigr\|^{p_z}
\right).
\end{equation}
In practice, the continuous physics residual term is approximated by quadrature. Let $S_{\mathrm{int}}=\{s_i\}_{i=1}^{N_{\mathrm{int}}}\subset I$ denote the collocation set, with positive quadrature weights $\{w_i\}_{i=1}^{N_{\mathrm{int}}}$. For the data term, we introduce positive weights $\{v_j\}_{j=1}^{N_d}$. The resulting discrete loss is
\begin{equation}
J(\phi,\boldsymbol{\theta})
=
\sum_{j=1}^{N_d} v_j
\bigl\|\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}_\phi](t_j)\bigr\|^{p_z}
-
\lambda
\sum_{i=1}^{N_{\mathrm{int}}} w_i
\bigl\|\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_\phi,\boldsymbol{\theta}](s_i)\bigr\|^{p_y},
\label{eq:loss}
\end{equation}
where $\lambda>0$ balances the data-misfit and physics-residual terms.

To further stabilize training, we may optionally include a regularization term on the network parameters as
\begin{equation}
(\hat{\phi},\hat{\boldsymbol{\theta}})
=
\arg\min_{(\phi,\boldsymbol{\theta})}
\Bigl(
J(\phi,\boldsymbol{\theta})+\lambda_{\mathrm{reg}}\,J_{\mathrm{reg}}(\phi)
\Bigr),
\label{eq:reg}
\end{equation}
where $J_{\mathrm{reg}}:\mathbb{R}^M\to\mathbb{R}$ is a regularization functional and $\lambda_{\mathrm{reg}}\ge 0$ is the corresponding penalty parameter. A common choice is $J_{\mathrm{reg}}(\phi)=\|\phi\|_q^q$, where $q=2$ gives standard $L^2$ regularization, while $q=1$ can be used to promote sparsity.

\subsection{Stage I: Coarse Localization via Residual Signature}
\label{subsec:stage1}

To obtain a coarse localization of the change-point, we partition the temporal domain into overlapping subintervals. Let
\begin{equation}
0=t_0<t_1<\cdots<t_K=T,
\end{equation}
be a partition of $I=[0,T]$, and let $\delta>0$ denote the overlap width. For each $k=1,\ldots,K$, we define
\begin{equation}
I_k=[t_{k-1}-\delta,\;t_k+\delta]\cap[0,T].
\end{equation}
By construction, every change-point $\tau\in(0,T)$ is contained in at least one such subinterval.

At this stage, the subinterval problems are treated independently. No interface or continuity conditions are imposed across overlapping regions, because the goal of Stage~I is change-point screening rather than global reconstruction. On each $I_k$, we train a local PINN $\boldsymbol{x}_{\phi_k}:I_k\to\mathbb{R}^n$ together with a locally constant parameter vector $\boldsymbol{\theta}_k\in\Theta$.

Let
\begin{equation}
S_k^r=\{s_i^{(k)}\}_{i=1}^{N_k^r}\subset I_k,
\quad
S_k^d=\{t_j^{(k)}\}_{j=1}^{N_k^d}\subset I_k\cap I_d,
\end{equation}
which denote the collocation set and the observation set on $I_k$, respectively. Let $\{w_i^{(k)}\}_{i=1}^{N_k^r}$ and $\{v_j^{(k)}\}_{j=1}^{N_k^d}$ be the associated positive weights. The local training objective is
\begin{equation}
\begin{aligned}
J_k(\phi_k,\boldsymbol{\theta}_k)
&=
\sum_{j=1}^{N_k^d} v_j^{(k)}
\bigl\|
\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}_{\phi_k}](t_j^{(k)})
\bigr\|^{p_z}
+
\lambda
\sum_{i=1}^{N_k^r} w_i^{(k)}
\bigl\|
\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_{\phi_k},\boldsymbol{\theta}_k](s_i^{(k)})
\bigr\|^{p_y}.
\end{aligned}
\label{eq:subinterval-loss}
\end{equation}

Since the local problems are uncoupled, all subinterval PINNs can be trained in parallel. The overlap is introduced to improve the robustness of change-point localization near subinterval boundaries.

After training on $I_k$, we compute the physics residual energy
\begin{equation}
E_k
=
\sum_{i=1}^{N_k^r} w_i^{(k)}
\bigl\|
\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_{\phi_k},\boldsymbol{\theta}_k](s_i^{(k)})
\bigr\|^{p_y}.
\label{eq:Ek_def}
\end{equation}
To make these energies comparable across subintervals, we normalize them by the total collocation weight and define
\begin{equation}
\bar E_k
=
\frac{E_k}{\sum_{i=1}^{N_k^r} w_i^{(k)}}.
\label{eq:Ek_normalized}
\end{equation}

Because PINN training may exhibit transient oscillations or occasional spikes, we summarize the terminal behavior of the normalized residual over the last $M$ iterations. Let $\bar E_{k,\ell}$ denote the value of \eqref{eq:Ek_normalized} at iteration $\ell$, and let
\begin{equation}
\mathcal W=\{L-M+1,\ldots,L\},
\end{equation}
where $L$ is the total number of training iterations. We then define
\begin{equation}
S_k=\operatorname{median}\{\bar E_{k,\ell}:\ell\in\mathcal W\}.
\label{eq:Sk_def}
\end{equation}
This score provides a robust summary of the terminal residual level on subinterval $I_k$.

The key observation underlying RAA-PINNs is that $S_k$ tends to be elevated when $I_k$ contains the change-point. If $I_k$ lies entirely on one side of $\tau$, then the dynamics on $I_k$ are governed by a single parameter regime, and a locally constant parameter vector can fit the subinterval well, leading to a relatively small residual level. By contrast, if $\tau\in I_k$, then the dynamics on $I_k$ involve two distinct parameter regimes associated with $\boldsymbol{\theta}^-$ and $\boldsymbol{\theta}^+$. Any single constant parameter vector $\boldsymbol{\theta}_k$ must then compromise between the two regimes, producing a residual-loss anomaly that cannot be removed by training.

To formalize this residual-loss anomaly mechanism, we introduce the following assumptions. These conditions are tailored to the present regime-switching setting and are closely related to standard identifiability assumptions in parameter estimation and consistency requirements in collocation and physics-informed formulations \cite{quarteroni2006numerical, raissi2019physics}.

\begin{assumption}[Parameter-affine structure and local identifiability]
\label{ass:structural}
Let $\boldsymbol{x}^\star:I\to\mathbb{R}^n$ denote the true trajectory. Assume that the vector field $\boldsymbol{f}:I\times\mathbb{R}^n\times\Theta\to\mathbb{R}^n$ is affine in the parameter vector $\boldsymbol{\theta}$, namely,
\begin{equation}
\boldsymbol{f}(t,\boldsymbol{x};\boldsymbol{\theta})
=
G(t,\boldsymbol{x})\boldsymbol{\theta}
+
\boldsymbol{b}(t,\boldsymbol{x}),
\end{equation}
where
\begin{equation}
G:I\times\mathbb{R}^n\to\mathbb{R}^{n\times m},
\quad
\boldsymbol{b}:I\times\mathbb{R}^n\to\mathbb{R}^n.
\end{equation}
Moreover, assume that there exists a constant $\alpha>0$ such that for every subinterval $J\subset I$ with positive length, the associated information matrix
\begin{equation}
M(J)
=
\int_J
G\bigl(t,\boldsymbol{x}^\star(t)\bigr)^\top
G\bigl(t,\boldsymbol{x}^\star(t)\bigr)\,{\rm d}t,
\end{equation}
satisfies
\begin{equation}
\lambda_{\min}\bigl(M(J)\bigr)\ge \alpha |J|,
\end{equation}
where $|J|$ denotes the length of $J$ and $\lambda_{\min}(\cdot)$ denotes the smallest eigenvalue.
\end{assumption}

\begin{assumption}[Quadrature consistency of the interior residual]
\label{ass:quadrature}
For each subinterval $I_k$, let $S_k^r=\{s_i^{(k)}\}_{i=1}^{N_k^r}\subset I_k$ be the collocation set, where $N_k^r$ is the number of collocation points in $I_k$, and let $\{w_i^{(k)}\}_{i=1}^{N_k^r}$ be the associated positive weights. Assume that the corresponding quadrature rule is consistent on $I_k$, in the sense that for any continuous function $h:I_k\to\mathbb{R}$,
\begin{equation}
\lim_{N_k^r\to\infty}
\sum_{i=1}^{N_k^r} w_i^{(k)}\,h\bigl(s_i^{(k)}\bigr)
=
\int_{I_k} h(t)\,{\rm d}t.
\end{equation}
\end{assumption}

Assumption~\ref{ass:structural} excludes degenerate regimes in which the dynamics are locally insensitive to the unknown parameters. Assumption~\ref{ass:quadrature} ensures that the discrete PINN residual provides a faithful approximation to its continuous-time counterpart. Under these conditions, the next theorem explains why the interior residual remains systematically larger on subintervals that cross the change-point. We denote by $\mathcal{R}_k$ the corresponding continuous-time residual energy on $I_k$.

\begin{theorem}[Residual lower bound on change-point subintervals]
\label{thm:lower_bound}
Under Assumption~\ref{ass:structural}, let $I_k$ be any Stage~I subinterval and define $I_k^- = I_k\cap[0,\tau)$ and $I_k^+ = I_k\cap[\tau,T]$. For any constant parameter vector $\boldsymbol{\theta}\in\Theta$, define the continuous-time residual energy
\begin{equation}
\mathcal{R}_k(\boldsymbol{\theta})
=
\int_{I_k}
\left\|
\frac{{\rm d}\boldsymbol{x}^\star}{{\rm d}t}(t)
-
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}\bigr)
\right\|_2^2
\,{\rm d}t,
\label{eq:Rk_theta}
\end{equation}
and let
\begin{equation}
\underline{\mathcal{R}}_k
=
\inf_{\boldsymbol{\theta}\in\Theta}\mathcal{R}_k(\boldsymbol{\theta}).
\label{eq:Rk_ideal}
\end{equation}
If $\tau\notin I_k$, then either $I_k^-=\emptyset$ or $I_k^+=\emptyset$, and hence $\underline{\mathcal{R}}_k=0$ in the absence of observational noise. If $\tau\in I_k$ and $\boldsymbol{\theta}^-\neq\boldsymbol{\theta}^+$, then
\begin{equation}
\underline{\mathcal{R}}_k
\;\ge\;
\alpha
\frac{|I_k^-|\,|I_k^+|}{|I_k^-|+|I_k^+|}
\,
\|\boldsymbol{\theta}^- - \boldsymbol{\theta}^+\|_2^2.
\label{eq:lower_bound_main}
\end{equation}
In particular,
\begin{equation}
\underline{\mathcal{R}}_k
\;\ge\;
\frac{\alpha}{2}\min\{|I_k^-|,|I_k^+|\}
\,
\|\boldsymbol{\theta}^- - \boldsymbol{\theta}^+\|_2^2.
\label{eq:lower_bound_main_simple}
\end{equation}
\end{theorem}

\begin{proof}
We consider separately the cases $\tau\notin I_k$ and $\tau\in I_k$.

First, suppose that $\tau\notin I_k$. If $I_k$ lies entirely on one side of the change-point, then the true dynamics on $I_k$ are governed by a single constant parameter vector $\boldsymbol{\theta}^{\mathrm{true}}\in\{\boldsymbol{\theta}^-,\boldsymbol{\theta}^+\}$, which means
\begin{equation}
\frac{{\rm d}\boldsymbol{x}^\star}{{\rm d}t}(t)
=
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}^{\mathrm{true}}\bigr),
\quad \forall\, t\in I_k.
\end{equation}
In the noise-free setting, choosing $\boldsymbol{\theta}=\boldsymbol{\theta}^{\mathrm{true}}$ in \eqref{eq:Rk_theta} yields
\begin{equation}
\mathcal{R}_k(\boldsymbol{\theta}^{\mathrm{true}})
=
\int_{I_k}
\bigl\|
\dot{\boldsymbol{x}}^\star(t)
-
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}^{\mathrm{true}}\bigr)
\bigr\|_2^2\,{\rm d}t
=
0.
\end{equation}
Hence,
\begin{equation}
\underline{\mathcal{R}}_k
=
\inf_{\boldsymbol{\theta}\in\Theta}\mathcal{R}_k(\boldsymbol{\theta})
=
0.
\end{equation}

We now turn to the case $\tau\in I_k$ and $\boldsymbol{\theta}^-\neq\boldsymbol{\theta}^+$. When the subinterval $I_k$ crosses the change-point, the true trajectory satisfies the piecewise dynamics
\begin{equation}
\dot{\boldsymbol{x}}^\star(t)
=
\begin{cases}
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}^-\bigr), & t\in I_k^-,\\[2pt]
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}^+\bigr), & t\in I_k^+.
\end{cases}
\end{equation}
For any candidate constant parameter vector $\boldsymbol{\theta}\in\Theta$, the corresponding residual energy admits the decomposition
\begin{equation}
\begin{aligned}
\mathcal{R}_k(\boldsymbol{\theta})
&=
\int_{I_k}
\bigl\|
\dot{\boldsymbol{x}}^\star(t)
-
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}\bigr)
\bigr\|_2^2\,{\rm d}t
\\
&=
\int_{I_k^-}
\bigl\|
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}^-\bigr)
-
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}\bigr)
\bigr\|_2^2\,{\rm d}t
+
\int_{I_k^+}
\bigl\|
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}^+\bigr)
-
\boldsymbol{f}\bigl(t,\boldsymbol{x}^\star(t);\boldsymbol{\theta}\bigr)
\bigr\|_2^2\,{\rm d}t .
\end{aligned}
\label{eq:residual-decomposition}
\end{equation}

By Assumption~\ref{ass:structural}, the vector field is affine in the parameter vector and can be written as
\begin{equation}
\boldsymbol{f}(t,\boldsymbol{x};\boldsymbol{\theta})
=
G(t,\boldsymbol{x})\boldsymbol{\theta}
+
\boldsymbol{b}(t,\boldsymbol{x}).
\end{equation}
Substituting this representation into \eqref{eq:residual-decomposition} and canceling the common offset term $\boldsymbol{b}(t,\boldsymbol{x}^\star(t))$ yields
\begin{equation}
\begin{aligned}
\mathcal{R}_k(\boldsymbol{\theta})
&=
\int_{I_k^-}
\bigl\|
G\bigl(t,\boldsymbol{x}^\star(t)\bigr)(\boldsymbol{\theta}^- - \boldsymbol{\theta})
\bigr\|_2^2\,{\rm d}t
+
\int_{I_k^+}
\bigl\|
G\bigl(t,\boldsymbol{x}^\star(t)\bigr)(\boldsymbol{\theta}^+ - \boldsymbol{\theta})
\bigr\|_2^2\,{\rm d}t
\\
&=
(\boldsymbol{\theta}^- - \boldsymbol{\theta})^\top
M(I_k^-)
(\boldsymbol{\theta}^- - \boldsymbol{\theta})
+
(\boldsymbol{\theta}^+ - \boldsymbol{\theta})^\top
M(I_k^+)
(\boldsymbol{\theta}^+ - \boldsymbol{\theta}),
\end{aligned}
\label{eq:quadratic-form}
\end{equation}
where, for any interval $J\subset I$,
\begin{equation}
M(J)
=
\int_J
G\bigl(t,\boldsymbol{x}^\star(t)\bigr)^\top
G\bigl(t,\boldsymbol{x}^\star(t)\bigr)
\,{\rm d}t
\end{equation}
denotes the associated information matrix.

Invoking Assumption~\ref{ass:structural}, there exists $\alpha>0$ such that for any relevant interval $J\subset I$,
\begin{equation}
\lambda_{\min}\bigl(M(J)\bigr)\ge \alpha |J|.
\end{equation}
Applying this bound to \eqref{eq:quadratic-form} gives
\begin{equation}
\mathcal{R}_k(\boldsymbol{\theta})
\;\ge\;
\alpha |I_k^-|\,\|\boldsymbol{\theta}^- - \boldsymbol{\theta}\|_2^2
+
\alpha |I_k^+|\,\|\boldsymbol{\theta}^+ - \boldsymbol{\theta}\|_2^2 .
\label{eq:lower-bound-theta}
\end{equation}

The right-hand side of \eqref{eq:lower-bound-theta} is a strictly convex quadratic function of $\boldsymbol{\theta}$. Define
\begin{equation}
Q(\boldsymbol{\theta})
=
|I_k^-|\,\|\boldsymbol{\theta}^- - \boldsymbol{\theta}\|_2^2
+
|I_k^+|\,\|\boldsymbol{\theta}^+ - \boldsymbol{\theta}\|_2^2 .
\end{equation}
A direct calculation shows that the unique minimizer of $Q$ over $\mathbb{R}^m$ is
\begin{equation}
\bar{\boldsymbol{\theta}}_k
=
\frac{|I_k^-|\boldsymbol{\theta}^-+|I_k^+|\boldsymbol{\theta}^+}{|I_k^-|+|I_k^+|}.
\end{equation}
Substituting $\bar{\boldsymbol{\theta}}_k$ back into $Q$ yields
\begin{equation}
\inf_{\boldsymbol{\theta}\in\mathbb{R}^m}Q(\boldsymbol{\theta})
=
\frac{|I_k^-|\,|I_k^+|}{|I_k^-|+|I_k^+|}
\,
\|\boldsymbol{\theta}^- - \boldsymbol{\theta}^+\|_2^2.
\end{equation}
Since $\Theta\subset\mathbb{R}^m$, it follows that
\begin{equation}
\inf_{\boldsymbol{\theta}\in\Theta}Q(\boldsymbol{\theta})
\;\ge\;
\inf_{\boldsymbol{\theta}\in\mathbb{R}^m}Q(\boldsymbol{\theta}).
\end{equation}
Combining this inequality with \eqref{eq:lower-bound-theta} and taking the infimum over $\boldsymbol{\theta}\in\Theta$ gives
\begin{equation}
\underline{\mathcal{R}}_k
=
\inf_{\boldsymbol{\theta}\in\Theta}\mathcal{R}_k(\boldsymbol{\theta})
\;\ge\;
\alpha
\frac{|I_k^-|\,|I_k^+|}{|I_k^-|+|I_k^+|}
\,
\|\boldsymbol{\theta}^- - \boldsymbol{\theta}^+\|_2^2,
\end{equation}
which proves \eqref{eq:lower_bound_main}.

Finally, since
\begin{equation}
\frac{ab}{a+b}\ge \frac12\min\{a,b\},
\quad a,b>0,
\end{equation}
we also obtain \eqref{eq:lower_bound_main_simple}. This completes the proof.
\end{proof}

\begin{remark}
Theorem~\ref{thm:lower_bound} provides the theoretical basis for Stage~I. It shows that any subinterval containing the true change-point must exhibit a strictly positive residual mismatch under a single constant-parameter fit. Hence, the elevated residual used in the screening step is not merely an empirical phenomenon, but a structural consequence of regime switching. Unlike purely statistical change-point criteria, the detection signal here arises directly from incompatibility with the governing dynamics.
\end{remark}

Theorem~\ref{thm:lower_bound} concerns an idealized continuous-time quantity defined along the true trajectory. In practice, the score $S_k$ in \eqref{eq:Sk_def} is the corresponding learned discrete counterpart and is also affected by approximation error, measurement noise, and quadrature error. Under Assumption~\ref{ass:quadrature}, together with sufficient network capacity and adequate training, these effects are reduced, so that the relative ordering of $\{S_k\}_{k=1}^K$ remains informative for identifying subintervals that contain the change-point.

To reduce sensitivity to global scaling and outliers across subintervals, we further standardize the scores $\{S_k\}_{k=1}^K$ using median absolute deviation (Mad) normalization. Let
\begin{equation}
\operatorname{Med}(S)=\operatorname{median}\{S_1,\dots,S_K\},
\end{equation}
and define
\begin{equation}
\operatorname{Mad}(S)
=
\operatorname{median}\bigl\{|S_k-\operatorname{Med}(S)|:k=1,\dots,K\bigr\}.
\end{equation}
We then set
\begin{equation}
Z_k
=
\frac{S_k-\operatorname{Med}(S)}
{\operatorname{Mad}(S)+\varepsilon},
\label{eq:zk_def}
\end{equation}
where $\varepsilon>0$ is a small numerical stabilization parameter.

We define the candidate index set by
\begin{equation}
\mathcal K_c=\{k: Z_k\ge \gamma\},
\end{equation}
and select
\begin{equation}
k^\star=\arg\max_{k\in\mathcal K_c} S_k.
\end{equation}
Finally, we define the candidate interval by
\begin{equation}
\mathcal I_c
=
I_{k^\star-1}\cup I_{k^\star}\cup I_{k^\star+1},
\end{equation}
with the obvious boundary truncation when $k^\star\in\{1,K\}$. By construction, $\mathcal I_c$ is a narrow region that is expected to contain the true change-point $\tau$ with high probability and is therefore used as the search region in Stage~II.


\subsection{Stage II: Joint Inference within Candidate Interval}
\label{sec:stage2}

Stage~I yields a candidate interval $\mathcal I_c=[t_L,t_R]$ rather than a point estimate of the change-point. In Stage~II of RAA-PINNs, we refine this coarse localization by treating the change-point as a trainable variable within a local PINN defined on $\mathcal I_c$.

To enforce the constraint $\tau\in(t_L,t_R)$ during optimization, we introduce an unconstrained scalar variable $\eta\in\mathbb{R}$ and define
\begin{equation}
\tau(\eta)
=
t_L+(t_R-t_L)\,\sigma(\eta),
\quad
\sigma(z)=\frac{1}{1+e^{-z}}.
\end{equation}
This reparameterization ensures that the change-point remains in the interior of $\mathcal I_c$ throughout the optimization process.

To enable gradient-based optimization with respect to $\tau$, we replace the discontinuous step profile with the smooth gating function
\begin{equation}
g(t;\tau,\kappa)
=
\sigma\bigl(\kappa(t-\tau)\bigr),
\end{equation}
where $\kappa>0$ is a prescribed sharpness parameter. Larger values of $\kappa$ yield a closer approximation to a hard change-point.

Using this gate, we introduce the time-dependent parameter vector
\begin{equation}
\boldsymbol{\theta}(t;\boldsymbol{\theta}^-,\boldsymbol{\theta}^+,\eta)
=
\boldsymbol{\theta}^-
+
(\boldsymbol{\theta}^+-\boldsymbol{\theta}^-)\,
g\bigl(t;\tau(\eta),\kappa\bigr),
\label{eq:theta_gate}
\end{equation}
which serves as a differentiable surrogate for the piecewise-constant parameterization in \eqref{eq:theta_piecewise}. In the limit $\kappa\to\infty$, this representation approaches a sharp transition.

We then train a new local PINN $\boldsymbol{x}_{\phi}:\mathcal I_c\to\mathbb{R}^n$ jointly with the variables $(\boldsymbol{\theta}^-,\boldsymbol{\theta}^+,\eta)$ in order to refine both the change-point location and the regime-specific parameters. Let
\begin{equation}
S_c^r=\{s_i^{(c)}\}_{i=1}^{N_c^r}\subset \mathcal I_c,
\quad
S_c^d=\{t_j^{(c)}\}_{j=1}^{N_c^d}\subset \mathcal I_c\cap I_d
\end{equation}
denote the collocation set and the observation set on $\mathcal I_c$, respectively. Let $\{w_i^{(c)}\}_{i=1}^{N_c^r}$ and $\{v_j^{(c)}\}_{j=1}^{N_c^d}$ be the associated positive weights.

The physics residual and the data residual under the gated parameterization are defined by
\begin{equation}
\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_\phi,\boldsymbol{\theta}(\cdot)](t)
=
\frac{{\rm d}\boldsymbol{x}_\phi}{{\rm d}t}(t)
-
\boldsymbol{f}\bigl(t,\boldsymbol{x}_\phi(t);\boldsymbol{\theta}(t;\boldsymbol{\theta}^-,\boldsymbol{\theta}^+,\eta)\bigr),
\quad t\in\mathcal I_c,
\end{equation}
and
\begin{equation}
\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}_\phi](t_j)
=
\boldsymbol{x}_\phi(t_j)-\boldsymbol{x}_d(t_j),
\quad t_j\in I_d\cap\mathcal I_c.
\end{equation}

We then minimize the local objective
\begin{equation}
\begin{aligned}
J_c(\phi,\boldsymbol{\theta}^-,\boldsymbol{\theta}^+,\eta)
&=
\sum_{j=1}^{N_c^d} v_j^{(c)}
\bigl\|
\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}_\phi](t_j^{(c)})
\bigr\|^{p_z}
+
\lambda
\sum_{i=1}^{N_c^r} w_i^{(c)}
\bigl\|
\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_\phi,\boldsymbol{\theta}(\cdot)](s_i^{(c)})
\bigr\|^{p_y},
\end{aligned}
\label{eq:stage2_loss}
\end{equation}
where $\lambda>0$ plays the same balancing role as in \eqref{eq:loss} and \eqref{eq:subinterval-loss}.

Let $(\hat\phi,\hat{\boldsymbol{\theta}}^-,\hat{\boldsymbol{\theta}}^+,\hat\eta)$ be any minimizer of \eqref{eq:stage2_loss}. The refined change-point estimate is then given by $\hat\tau=\tau(\hat\eta)$, while $\hat{\boldsymbol{\theta}}^-$ and $\hat{\boldsymbol{\theta}}^+$ are the corresponding parameter estimates on the two sides of the transition.

By construction, Stage~II converts the interval-level output of Stage~I into a pointwise change-point estimate through a differentiable parameterization on the reduced temporal region $\mathcal I_c$, while simultaneously recovering the parameter vectors before and after the transition.

\subsection{Theoretical Error Analysis}
\label{sec:error_analysis}

In this section, we analyze the approximation error of the PINN-based inverse solution for the ODE system ${\rm d}\boldsymbol{x}(t)=\boldsymbol{f}\bigl(t,\boldsymbol{x}(t);\boldsymbol{\theta}\bigr){\rm d}t$ in the presence of measurement data. This analysis provides a generalization-error interpretation for the local physics-informed inverse module underlying RAA-PINNs. Our argument follows the general philosophy of physics-informed inverse learning and conditional-stability-based generalization estimates \cite{mishra2022estimates}.

Let $\hat{\boldsymbol{x}}:=\boldsymbol{x}_{\phi}$ denote the learned PINN approximation of the state trajectory. Let $I'\subset I$ and let $1\le p_x,p_y,p_z<\infty$. Let $S^r=\{s_i\}_{i=1}^{N_r}\subset I$ be the collocation set for the physics residual, and let $S^d=\{t_j\}_{j=1}^{N_d}\subset I'$ be the data set associated with the measurement locations. We denote the corresponding positive quadrature weights by $\{w_i\}_{i=1}^{N_r}$ and $\{v_j\}_{j=1}^{N_d}$, respectively.

For any interval $E\subset I$, we define the generalization error by
\begin{equation}
\mathcal{E}_G(E)
=
\mathcal{E}_G(E;\phi,S^r,S^d)
=
\|\hat{\boldsymbol{x}}-\boldsymbol{x}\|_{L^{p_x}(E)}.
\label{eq:generalization_error}
\end{equation}
As indicated above, the generalization error depends on the training sets $S^r$, $S^d$, as well as on the network parameter $\phi$.

We next define the training residuals as
\begin{equation}\label{eq:training_errors}
\mathcal{E}_{r,T}(\boldsymbol{\theta},S^r)
=
\left(
\sum_{i=1}^{N_r}
w_i\,
\bigl\|
\mathcal{R}_{\mathrm{int}}[\hat{\boldsymbol{x}},\boldsymbol{\theta}](s_i)
\bigr\|^{p_y}
\right)^{1/p_y}, \quad
\mathcal{E}_{d,T}(S^d)
=
\left(
\sum_{j=1}^{N_d}
v_j\,
\bigl\|
\mathcal{R}_{\mathrm{data}}[\hat{\boldsymbol{x}}](t_j)
\bigr\|^{p_z}
\right)^{1/p_z},
\end{equation}
where $\mathcal{R}_{\mathrm{int}}$ and $\mathcal{R}_{\mathrm{data}}$ are defined in \eqref{eq:residuals-ode}. The quantity $\mathcal{E}_{r,T}$ measures the discrete physics residual, while $\mathcal{E}_{d,T}$ measures the discrepancy with the observations.

\begin{assumption}[Conditional stability]
\label{ass:ode_conditional_stability}
Let $\hat X\subset X^\ast\subset X=L^{p_x}(I)$ be Banach spaces. For any $u,v\in\hat X$, assume that the differential operator $\mathcal D$ and the restriction operator $\mathcal L$ satisfy
\begin{equation}
\|u-v\|_{L^{p_x}(E)}
\le
C_{pd}\!\bigl(\|u\|_{\hat X},\|v\|_{\hat X}\bigr)
\Bigl(
\|\mathcal D(u,\boldsymbol{\theta})-\mathcal D(v,\boldsymbol{\theta}')\|_{Y}^{\rho_p}
+
\|\mathcal L(u)-\mathcal L(v)\|_{Z}^{\rho_d}
\Bigr),
\label{eq:ode_conditional_stability}
\end{equation}
for some $0<\rho_p,\rho_d\le 1$ and any subset $I'\subset E\subset I$, where $Y=L^{p_y}(I)$ and $Z=L^{p_z}(I')$. Here
\begin{equation}
\mathcal D(\boldsymbol{x},\boldsymbol{\theta})(t)
=
\frac{{\rm d}\boldsymbol{x}}{{\rm d}t}(t)
-
\boldsymbol{f}\bigl(t,\boldsymbol{x}(t);\boldsymbol{\theta}\bigr),
\quad
\mathcal L(\boldsymbol{x})
=
\boldsymbol{x}\big|_{I'}.
\end{equation}
\end{assumption}

Let $S^r=\{s_i\}_{i=1}^{N_r}\subset I$ be quadrature points with weights $w_i\in\mathbb R_+$. For a function $h:I\to\mathbb R$, define the quadrature functional
\begin{equation}
Q_r^N(h)
=
\sum_{i=1}^{N_r} w_i\,h(s_i).
\label{eq:ode_quadrature_int}
\end{equation}
Assume that the corresponding quadrature error satisfies
\begin{equation}
\left|
\int_I h(t)\,{\rm d}t
-
Q_r^N(h)
\right|
\le
C_q\bigl(\|h\|_{Y,\bar d}\bigr)\,N_r^{-\alpha},
\quad \text{for some }\alpha>0,
\label{eq:ode_quadrature_int_error}
\end{equation}
where $\bar d$ denotes the regularity index required by the quadrature rule.

Similarly, let $S^d=\{t_j\}_{j=1}^{N_d}\subset I'$ be quadrature points for the data term with weights $v_j\in\mathbb R_+$. For a function $h_d:I'\to\mathbb R$, define
\begin{equation}
Q_d^N(h_d)
=
\sum_{j=1}^{N_d} v_j\,h_d(t_j).
\label{eq:ode_quadrature_data}
\end{equation}
Assume that the corresponding quadrature error satisfies
\begin{equation}
\left|
\int_{I'} h_d(t)\,{\rm d}t
-
Q_d^N(h_d)
\right|
\le
C_{qd}\!\bigl(\|h_d\|_{Z,\bar d}\bigr)\,N_d^{-\alpha_d},
\quad \text{for some }\alpha_d>0.
\label{eq:ode_quadrature_data_error}
\end{equation}
Then the following theorem bounds the generalization error in terms of the discrete training residuals and the quadrature errors, in the spirit of the conditional-stability-based PINN analysis in \cite{qian2023physics}.

\begin{theorem}[PINN generalization error estimate for ODE inverse problems]
\label{thm:ode-gen-error}
Let $\boldsymbol{x}\in\hat X\subset X^\ast\subset X$ be the solution of the inverse problem associated with \eqref{eq:3.6}, and assume that the stability estimate \eqref{eq:ode_conditional_stability} holds for any $I'\subset E\subset I$. Let $\hat{\boldsymbol{x}}\in\hat X$ be a PINN approximation generated from the training sets $S^r$ and $S^d$. Assume further that $\|\mathcal{R}_{\mathrm{int}}[\hat{\boldsymbol{x}},\hat{\boldsymbol{\theta}}](\cdot)\|^{p_y}\in Y$ and $\|\mathcal{R}_{\mathrm{data}}[\hat{\boldsymbol{x}}](\cdot)\|^{p_z}\in Z$, and that the quadrature errors satisfy \eqref{eq:ode_quadrature_int_error} and \eqref{eq:ode_quadrature_data_error}. Then
\begin{equation}
\mathcal{E}_G(E)
\le
C_{pd}\Bigl(
\mathcal{E}_{r,T}(\hat{\boldsymbol{\theta}},S^r)^{\rho_p}
+
\mathcal{E}_{d,T}(S^d)^{\rho_d}
+
C_q\,N_r^{-\alpha\rho_p/p_y}
+
C_{qd}\,N_d^{-\alpha_d\rho_d/p_z}
\Bigr),
\label{eq:EG-bound-ode-final}
\end{equation}
where
\begin{equation}
C_{pd}
=
C_{pd}\bigl(\|\boldsymbol{x}\|_{\hat X},\|\hat{\boldsymbol{x}}\|_{\hat X}\bigr),
\quad
C_q
=
C_q\Bigl(
\bigl\|
\|\mathcal{R}_{\mathrm{int}}[\hat{\boldsymbol{x}},\hat{\boldsymbol{\theta}}](\cdot)\|^{p_y}
\bigr\|_{Y}
\Bigr),
\quad
C_{qd}
=
C_{qd}\Bigl(
\bigl\|
\|\mathcal{R}_{\mathrm{data}}[\hat{\boldsymbol{x}}](\cdot)\|^{p_z}
\bigr\|_{Z}
\Bigr).
\end{equation}
\end{theorem}

\begin{proof}
For notational simplicity, define
\begin{equation}
\mathcal R
=
\mathcal D(\hat{\boldsymbol{x}},\hat{\boldsymbol{\theta}}),
\quad
\mathcal R_d
=
\mathcal L(\hat{\boldsymbol{x}})-\boldsymbol{x}\big|_{I'}.
\end{equation}
Since $(\boldsymbol{x},\boldsymbol{\theta})$ solves \eqref{eq:3.6}, we have $\mathcal D(\boldsymbol{x},\boldsymbol{\theta})\equiv 0$, and therefore
\begin{equation}
\mathcal R
=
\mathcal D(\hat{\boldsymbol{x}},\hat{\boldsymbol{\theta}})
-
\mathcal D(\boldsymbol{x},\boldsymbol{\theta}).
\label{eq:ode_R_as_operator_diff}
\end{equation}
Similarly, because $\mathcal L(\boldsymbol{x})=\boldsymbol{x}|_{I'}$, it follows that
\begin{equation}
\mathcal R_d
=
\mathcal L(\hat{\boldsymbol{x}})
-
\mathcal L(\boldsymbol{x}).
\label{eq:ode_Rd_as_operator_diff}
\end{equation}

Applying the conditional stability estimate \eqref{eq:ode_conditional_stability} with $u=\hat{\boldsymbol{x}}$ and $v=\boldsymbol{x}$ gives
\begin{align}
\mathcal E_G(E)
=
\|\hat{\boldsymbol{x}}-\boldsymbol{x}\|_{L^{p_x}(E)}
&\le
C_{pd}\Bigl(
\|\mathcal D(\hat{\boldsymbol{x}},\hat{\boldsymbol{\theta}})
-
\mathcal D(\boldsymbol{x},\boldsymbol{\theta})\|_{Y}^{\rho_p}
+
\|\mathcal L(\hat{\boldsymbol{x}})-\mathcal L(\boldsymbol{x})\|_{Z}^{\rho_d}
\Bigr)
\notag\\
&=
C_{pd}\Bigl(
\|\mathcal R\|_{Y}^{\rho_p}
+
\|\mathcal R_d\|_{Z}^{\rho_d}
\Bigr).
\label{eq:ode_step_stability_to_residuals}
\end{align}

We next bound the two residual norms by their discrete training counterparts. Since $Y=L^{p_y}(I)$, applying the quadrature estimate \eqref{eq:ode_quadrature_int_error} to $h(t)=\|\mathcal R(t)\|^{p_y}$ yields
\begin{equation}
\|\mathcal R\|_{Y}^{p_y}
=
\int_I \|\mathcal R(t)\|^{p_y}\,{\rm d}t
\le
\sum_{i=1}^{N_r} w_i\,\|\mathcal R(s_i)\|^{p_y}
+
C_q N_r^{-\alpha}
=
\mathcal E_{r,T}(\hat{\boldsymbol{\theta}},S^r)^{p_y}
+
C_q N_r^{-\alpha}.
\end{equation}
Since $0<\rho_p\le 1$, we use the subadditivity of $a\mapsto a^{\rho_p/p_y}$ on $\mathbb R_+$ to obtain
\begin{equation}
\|\mathcal R\|_{Y}^{\rho_p}
\le
\mathcal E_{r,T}(\hat{\boldsymbol{\theta}},S^r)^{\rho_p}
+
C_q^{\rho_p/p_y} N_r^{-\alpha\rho_p/p_y}.
\label{eq:ode_step_quad_int}
\end{equation}

Similarly, since $Z=L^{p_z}(I')$, applying \eqref{eq:ode_quadrature_data_error} to $h_d(t)=\|\mathcal R_d(t)\|^{p_z}$ gives
\begin{equation}
\|\mathcal R_d\|_{Z}^{p_z}
=
\int_{I'} \|\mathcal R_d(t)\|^{p_z}\,{\rm d}t
\le
\sum_{j=1}^{N_d} v_j\,\|\mathcal R_d(t_j)\|^{p_z}
+
C_{qd} N_d^{-\alpha_d}
=
\mathcal E_{d,T}(S^d)^{p_z}
+
C_{qd} N_d^{-\alpha_d}.
\end{equation}
Again, since $0<\rho_d\le 1$,
\begin{equation}
\|\mathcal R_d\|_{Z}^{\rho_d}
\le
\mathcal E_{d,T}(S^d)^{\rho_d}
+
C_{qd}^{\rho_d/p_z} N_d^{-\alpha_d\rho_d/p_z}.
\label{eq:ode_step_quad_data}
\end{equation}

Substituting \eqref{eq:ode_step_quad_int} and \eqref{eq:ode_step_quad_data} into \eqref{eq:ode_step_stability_to_residuals} yields \eqref{eq:EG-bound-ode-final}.
\end{proof}

This bound also suggests a natural notion of a well-trained PINN, namely the regime in which the discrete training residuals are of the same order as, or smaller than, the quadrature-induced generalization gap as
\begin{equation}
\max\Bigl\{
\mathcal E_{r,T}(\hat{\boldsymbol{\theta}},S^r)^{\rho_p},
\mathcal E_{d,T}(S^d)^{\rho_d}
\Bigr\}
\le
C_q^{\rho_p/p_y}N_r^{-\alpha\rho_p/p_y}
+
C_{qd}^{\rho_d/p_z}N_d^{-\alpha_d\rho_d/p_z}.
\label{eq:ode_well_trained}
\end{equation}
In this regime, the dominant contribution to the generalization error comes from discretization and quadrature rather than incomplete optimization.

\begin{remark}
Estimate \eqref{eq:EG-bound-ode-final} decomposes the generalization error into contributions from training residuals and quadrature approximation under a conditional-stability framework. In particular, it links the PINN error explicitly to both optimization accuracy and sampling complexity. In the context of RAA-PINNs, this result provides theoretical support for the reliability of the local physics-informed inverse modules used in residual-based screening and local refinement.
\end{remark}

We further show that a parameter jump induces a non-vanishing post-change physics residual when the post-change dynamics are evaluated with a mismatched constant parameter in following theorem.

\begin{theorem}[Post-change residual lower bound under parameter mismatch]
\label{thm:ode-change-residual-lower-bound}
Suppose that the true parameter satisfies \eqref{eq:theta_piecewise}. Let
$E_{+}\subset I\cap[\tau,T]$, $S^r_{+}=S^r\cap E_{+}$, and
$N_{r,+}=|S^r_{+}|$. For any $\tilde{\boldsymbol{\theta}}\in\Theta$, assume that there exists $\gamma_{+}>0$ such that
\begin{equation}
\left\|
\boldsymbol f(\cdot,\boldsymbol{x}(\cdot);\boldsymbol{\theta}^{+})
-
\boldsymbol f(\cdot,\boldsymbol{x}(\cdot);\tilde{\boldsymbol{\theta}})
\right\|_{L^{p_y}(E_{+})}
\ge
\gamma_{+}
\|\boldsymbol{\theta}^{+}-\tilde{\boldsymbol{\theta}}\|.
\label{eq:post_change_identifiability_short}
\end{equation}
Define
\begin{equation}
\varepsilon_{+}
=
\|\dot{\hat{\boldsymbol{x}}}-\dot{\boldsymbol{x}}\|_{L^{p_y}(E_{+})}
+
L\|\hat{\boldsymbol{x}}-\boldsymbol{x}\|_{L^{p_y}(E_{+})}.
\label{eq:post_change_approx_error_short}
\end{equation}
Then
\begin{equation}
\left\|
\mathcal D(\hat{\boldsymbol{x}},\tilde{\boldsymbol{\theta}})
\right\|_{L^{p_y}(E_{+})}
\ge
\Bigl(
\gamma_{+}\|\boldsymbol{\theta}^{+}-\tilde{\boldsymbol{\theta}}\|
-
\varepsilon_{+}
\Bigr)_{+}.
\label{eq:continuous_residual_lower_bound_short}
\end{equation}
Moreover, if \eqref{eq:ode_quadrature_int_error} holds on $E_{+}$ with constant $C_{q,+}$, then
\begin{equation}
\mathcal E_{r,T}(\tilde{\boldsymbol{\theta}},S^r_{+})
\ge
\left[
\Bigl(
\gamma_{+}\|\boldsymbol{\theta}^{+}-\tilde{\boldsymbol{\theta}}\|
-
\varepsilon_{+}
\Bigr)_{+}^{p_y}
-
C_{q,+}N_{r,+}^{-\alpha}
\right]_{+}^{1/p_y}.
\label{eq:discrete_residual_lower_bound_short}
\end{equation}
In particular, for $\tilde{\boldsymbol{\theta}}=\boldsymbol{\theta}^{-}$, the post-change residual is bounded from below by the jump size
$\|\boldsymbol{\theta}^{+}-\boldsymbol{\theta}^{-}\|$ up to approximation and quadrature errors.
\end{theorem}

\begin{proof}
On $E_{+}$, the true trajectory satisfies
\begin{equation}
\dot{\boldsymbol{x}}(t)
=
\boldsymbol f(t,\boldsymbol{x}(t);\boldsymbol{\theta}^{+}).
\end{equation}
Hence, for any $\tilde{\boldsymbol{\theta}}\in\Theta$,
\begin{align}
\mathcal D(\hat{\boldsymbol{x}},\tilde{\boldsymbol{\theta}})
&=
\dot{\hat{\boldsymbol{x}}}
-
\boldsymbol f(t,\hat{\boldsymbol{x}};\tilde{\boldsymbol{\theta}})
\notag\\
&=
\dot{\hat{\boldsymbol{x}}}
-
\dot{\boldsymbol{x}}
+
\boldsymbol f(t,\boldsymbol{x};\boldsymbol{\theta}^{+})
-
\boldsymbol f(t,\boldsymbol{x};\tilde{\boldsymbol{\theta}})
+
\boldsymbol f(t,\boldsymbol{x};\tilde{\boldsymbol{\theta}})
-
\boldsymbol f(t,\hat{\boldsymbol{x}};\tilde{\boldsymbol{\theta}}).
\end{align}
Using the reverse triangle inequality, the Lipschitz condition \eqref{Lipschitz_condition}, and
\eqref{eq:post_change_identifiability_short}, we obtain
\begin{align}
\left\|
\mathcal D(\hat{\boldsymbol{x}},\tilde{\boldsymbol{\theta}})
\right\|_{L^{p_y}(E_{+})}
&\ge
\left\|
\boldsymbol f(\cdot,\boldsymbol{x};\boldsymbol{\theta}^{+})
-
\boldsymbol f(\cdot,\boldsymbol{x};\tilde{\boldsymbol{\theta}})
\right\|_{L^{p_y}(E_{+})}
\notag -
\|\dot{\hat{\boldsymbol{x}}}-\dot{\boldsymbol{x}}\|_{L^{p_y}(E_{+})}
-
L\|\hat{\boldsymbol{x}}-\boldsymbol{x}\|_{L^{p_y}(E_{+})}
\notag\\
&\ge
\gamma_{+}\|\boldsymbol{\theta}^{+}-\tilde{\boldsymbol{\theta}}\|
-
\varepsilon_{+}.
\end{align}
Taking the positive part gives \eqref{eq:continuous_residual_lower_bound_short}.

It remains to pass from the continuous residual to the discrete training residual. Applying the quadrature estimate on $E_{+}$ to
$h(t)=\|\mathcal D(\hat{\boldsymbol{x}},\tilde{\boldsymbol{\theta}})(t)\|^{p_y}$ gives
\begin{equation}
\mathcal E_{r,T}(\tilde{\boldsymbol{\theta}},S^r_{+})^{p_y}
\ge
\left\|
\mathcal D(\hat{\boldsymbol{x}},\tilde{\boldsymbol{\theta}})
\right\|_{L^{p_y}(E_{+})}^{p_y}
-
C_{q,+}N_{r,+}^{-\alpha}.
\end{equation}
Combining this inequality with \eqref{eq:continuous_residual_lower_bound_short} yields
\eqref{eq:discrete_residual_lower_bound_short}.
\end{proof}

\begin{remark}
Theorem \ref{thm:ode-change-residual-lower-bound} states that, after a parameter jump, using a pre-change or mismatched parameter necessarily generates a positive post-change physics residual whenever the jump magnitude dominates approximation and quadrature errors. This provides a theoretical justification for locating change points by detecting elevated physics residual losses after candidate transition times.
\end{remark}

In summary, this section establishes the RAA-PINNs framework for change-point detection and parameter recovery in nonlinear dynamical systems with regime switching. The proposed method combines local physics-informed inverse learning, residual-loss-anomaly-based coarse localization, and differentiable local refinement within a unified optimization framework. The theoretical analysis further shows that PINN generalization error can be controlled by training residuals and quadrature errors, while parameter jumps induce non-vanishing physics residuals under mismatched regimes. These results provide the mathematical foundation for using residual loss as an intrinsic signal of change points. In the next section, we validate the proposed framework on representative nonlinear dynamical systems and examine its performance in both change-point localization and parameter estimation.

\section{Numerical Experiment}\label{sec4}
In this section, we evaluate the performance of the proposed RAA-PINNs method for change-point detection and parameter estimation in nonlinear dynamical systems. We consider five representative systems: the Malthus model, the logistic model, the Van der Pol oscillator, the Lotka-Volterra model, and the Lorenz system. 

For all experiments, the time domain is divided into overlapping subintervals, and local PINNs are trained independently in each subinterval. Each network is a fully connected feedforward network, taking time as input and system state variables as output. The baseline network has 4 hidden layers with 64 neurons per layer. In the refinement stage, the width is increased to 80. All networks use the \texttt{tanh} activation function. The loss function includes both a data fitting term and a physics-informed residual term with equal weights. Training is performed using the Adam optimizer, with learning rates of $5 \times 10^{-3}$ for network parameters and $10^{-3}$ for physical parameters. In the refinement stage, a three-step training procedure is used: network pre-training, optimization of change-point positions, and joint optimization of parameters and change points. Change points are parameterized using a sigmoid function and linked with smooth transitions to ensure differentiability and numerical stability during optimization.

\subsection{Malthus and Logistic Model}

Population growth is a classical topic in dynamical systems, describing the temporal evolution of biological populations. Such models are widely used in ecology, demography, and resource management. Two representative models are Malthus and logistic models. In this work, we employ the RAA-PINNs to jointly estimate time-varying parameters and detect change points, illustrating the application of our framework to NDS-CPD.

The Malthusian model describes exponential population growth assuming unlimited resources. It is expressed as a one-dimensional ordinary differential equation:
\begin{equation}
\frac{{\rm d}P_m}{{\rm d}t} = r_m P_m,
\end{equation}
where $P_m$ denotes the population at time $t$, and $r_m$ is the population growth rate. In the context of a single-regime ODE, we denote $\boldsymbol{x}(t) = P_m(t)$ and $\boldsymbol{\theta} = r_m$ following the traditional nonmixture model formulation \eqref{eq:3.5}. We extend this model to a time-varying setting with multiple change points, using RAA-PINNs to jointly estimate the piecewise parameter $r_m(t)$ and detect change points.


\begin{figure}[t]
    \centering
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/output_of_malthus.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/sample_path_malthus.pdf}
    \end{minipage}

    \vspace{0.1em}

    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/Malthus_loss.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/p_m.pdf}
    \end{minipage}

    \caption{Malthus model. Top row: the output of $P_m(t)$ over $[0,100]$ (left) and the corresponding sample path (right). Bottom row: Stage~I identifies the candidate change-point interval determined from the physical loss in the overlapping domain (left), and Stage~II results for refined parameter estimation and change-point localization (right).}
    \label{fig:malthus}
\end{figure}


To illustrate, we introduce a discrete state variable $r(t)$ to represent the regime switching over the temporal domain $[0,T]$ with $T=100$. Let $\mathbb{I} = \{1,2\}$, and define
\begin{equation}
r(t) =
\begin{cases}
1, & 0 \le t < 40, \\
2, & 40 \le t \le 100.
\end{cases}
\end{equation}
Accordingly, the temporal evolution of $r(t)$ follows $r(t): 1 \rightarrow 2$. The piecewise population growth rate is
\begin{equation}
\boldsymbol{\theta}(t) =
\begin{cases}
0.1, & r(t) = 1, \\
0.05, & r(t) = 2.
\end{cases}
\end{equation}

In Stage I, the temporal domain is divided into overlapping subintervals for coarse change-point localization. The candidate change-point intervals identified by the elevated physical loss are $[39, 41],$ which fully cover the true change point at $t = 40$. Stage II refines this interval to jointly estimate the precise change-point location and the piecewise parameter values. The system output, sample path, and residual results are shown in Figure~\ref{fig:malthus}.


\begin{figure}[t]
    \centering
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/output_of_logistic.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/sample_path_logistic.pdf}
    \end{minipage}

    \vspace{0.1em}

    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/logistic_loss.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/p_l.pdf}
    \end{minipage}
    \caption{Logistic model. Top row: the output of $P_l(t)$ over $[0,100]$ (left) and the corresponding sample path (right). Bottom row: Stage~I candidate change-point interval (left) and Stage~II refined parameter estimation and change-point localization (right).}
    \label{Logistic}
\end{figure}

The logistic model incorporates environmental carrying capacity to capture the transition from rapid growth to a stable population. It is described by
\begin{equation}
\frac{{\rm d}P_l}{{\rm d}t} = r_l P_l \left( 1 - \frac{P_l}{Q} \right),
\end{equation}
where $P_l$ denotes the population at time $t$, $r_l$ is the growth rate, and $Q$ is the carrying capacity. In a single-regime ODE, $\boldsymbol{x}(t) = P_l(t)$ and $\boldsymbol{\theta} = r_l$.

We consider a time-varying logistic equation with a change point. Introducing a discrete state variable $r(t)$ over $[0,T]$ with $T=100$:
\begin{equation}
r(t) =
\begin{cases}
1, & 0 \le t < 60, \\
2, & 60 \le t \le 100.
\end{cases}
\end{equation}
The piecewise parameter vector is
\begin{equation}
\boldsymbol{\theta}(t) =
\begin{cases}
0.1, & r(t) = 1, \\
0.05, & r(t) = 2.
\end{cases}
\end{equation}

In Stage I, the candidate change-point interval identified by the elevated physical loss is $[59, 61],$ covering the true change point at $t=60$. Stage II jointly refines this interval to estimate the precise change-point location and parameter values. The system output, sample path, and residuals are shown in Figure~\ref{Logistic}.

For both models, the time interval is $[0,100]$ with window length 2 and step size 1. All observations within each overlapping domain are used to estimate parameters independently with RAA-PINNs. Elevated physical loss in domains containing change points determines Stage I candidate intervals, which Stage II refines to obtain precise change-point locations and parameter estimates. Detailed statistical inference and mean square errors are reported in Tables~\ref{tab:combined_parameter_estimation} and~\ref{tab:combined_change_points}. This example demonstrates that RAA-PINNs can recover time-varying parameters in simple exponential growth systems, illustrating the method's effectiveness in identifying abrupt transitions in linear population dynamics.

\begin{table}[t]
\centering
\caption{Parameter estimation results for different numerical examples.}
\label{tab:combined_parameter_estimation}

\small
\renewcommand{\arraystretch}{1.0}
\setlength{\tabcolsep}{6pt}

\begin{tabular}{
w{c}{2.5cm}
w{c}{2cm}
w{c}{2cm}
w{c}{2cm}
w{c}{2.5cm}
w{c}{2.5cm}
}

\toprule
\makecell[c]{Numerical\\[-3pt] Example}
& \makecell[c]{Equation\\[-3pt] Coefficient}
& \makecell[c]{Time}
& \makecell[c]{True\\[-3pt] Value}
& \makecell[c]{Parameter\\[-3pt] Estimation}
& \makecell[c]{Squared\\[-3pt] Error} \\
\midrule

% ===== Malthus =====
\multirow{2}{*}{\makecell[c]{Malthus}}
& \multirow{2}{*}{$r_m$} & $[0,40]$   & 0.1  & 0.0972 & $7.840\times 10^{-6}$ \\
&       & $[40,100]$ & 0.05 & 0.0487 & $1.690\times 10^{-6}$ \\

\midrule

% ===== Logistic =====
\multirow{2}{*}{\makecell[c]{Logistic}}
& \multirow{2}{*}{$r_l$} & $[0,60]$   & 0.1  & 0.0947 & $2.809\times 10^{-5}$ \\
&       & $[60,100]$ & 0.05 & 0.0435 & $4.225\times 10^{-5}$ \\

\midrule

% ===== Van der Pol =====
\multirow{3}{*}{\makecell[c]{Van der Pol}}
& \multirow{3}{*}{$\mu$} & $[0,40]$   & 1   & 1.0238 & $5.664\times 10^{-4}$ \\
&       & $[40,80]$  & 0.1 & 0.0912 & $7.744\times 10^{-5}$ \\
&       & $[80,100]$ & 0.5 & 0.4878 & $1.488\times 10^{-4}$ \\

\bottomrule
\end{tabular}
\end{table}

\subsection{Van der Pol Oscillator}

The Van der Pol oscillator is a canonical self-excited nonlinear oscillatory system, originally developed to model electronic circuits. Due to its simple structure yet rich nonlinear behavior, it has become a standard benchmark for studying nonlinear oscillations and stable limit-cycle dynamics, and is widely used in circuits, mechanical systems, and biological rhythms. In this work, we apply RAA-PINNs to estimate time-varying parameters and detect change points, illustrating its application to NDS-CPD.

The oscillator is governed by the second-order differential equation:
\begin{equation}
    \frac{{\rm d}^{2}v}{{\rm d}t^{2}} - \mu\bigl(1 - v^{2}\bigr)\frac{{\rm d}v}{{\rm d}t} + v = 0.
\end{equation}
This equation can be equivalently expressed as a first-order system:
\begin{equation}
\begin{cases}
\dfrac{{\rm d}M}{{\rm d}t} = N,\\[1mm]
\dfrac{{\rm d}N}{{\rm d}t}= \mu (1 - M^{2}) N - M,
\end{cases}
\end{equation}
where $\boldsymbol{x}(t) = (M(t), N(t))^\top$ and $\boldsymbol{\theta}(t) = \mu(t)$ in the traditional nonmixture ODE model \eqref{eq:3.5}.

We consider a Van der Pol oscillator with a piecewise time-varying parameter $\mu(t)$ exhibiting multiple change points. A discrete state variable $r(t)$ with state space $\mathbb{I}$ is introduced to characterize the parameter switching. Let $\mathbb{I} = \{1,2,3\}$ and $T=100$, and define
\begin{equation}
r(t) =
\begin{cases}
1, & 0 \le t < 40,\\
2, & 40 \le t < 80,\\
3, & 80 \le t \le 100.
\end{cases}
\end{equation}
Accordingly, the temporal evolution of $r(t)$ is $1 \to 2 \to 3$, and the piecewise parameter $\boldsymbol{\theta}(t)$ is
\begin{equation}
\boldsymbol{\theta}(t) =
\begin{cases}
1, & r(t) = 1,\\
0.1, & r(t) = 2,\\
0.5, & r(t) = 3.
\end{cases}
\label{true mu}
\end{equation}

The system output and sample paths are shown in Figure~\ref{van der pol}.

\begin{figure}[t]
    \centering
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/output_of_vanderpol.pdf}
    \end{minipage}%
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/sample_path_vanderpol.pdf}
    \end{minipage}

    \vspace{0.1em}

    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/vanderpol_loss.pdf}
    \end{minipage}%
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/mu.pdf}
    \end{minipage}
    \caption{Van der Pol oscillator model. Top row: the output of $(M(t), N(t))$ over $[0,100]$ (left) and the corresponding sample path (right). Bottom row: Stage~I results show candidate change-point intervals determined from the physical loss in the overlapping domain (left), and Stage~II results for parameter estimation and change-point localization (right).}
    \label{van der pol}
\end{figure}

In this model, the time interval is set to $[0,100]$ with a window length of 2 and a step size of 1. In Stage~I, each window is independently trained for 30,000 iterations to estimate the local constant parameter $\mu$, and candidate transition intervals are identified based on the physical residual. Specifically, the Stage~I candidate change-point intervals are $[39,41]$ and $[79,81]$, fully covering the true change points. In Stage~II, these candidate intervals are refined to jointly optimize the transition locations and the piecewise parameters, demonstrating that RAA-PINNs can robustly recover parameter variations and accurately identify change points in nonlinear dynamical systems.

Within each overlapping domain, all available observation data are used to estimate parameters independently. Elevated physical loss in domains containing change points is averaged over the last 100 training iterations to determine the Stage~I candidate intervals. The Stage~II optimization then produces the final parameter estimates and refined change-point locations. Detailed prediction errors, statistical inference results, and mean square errors for parameter recovery and change-point detection are reported in Tables~\ref{tab:combined_parameter_estimation} and~\ref{tab:combined_change_points}.

This case illustrates that RAA-PINNs can recover parameters in self-excited nonlinear oscillatory systems, demonstrating the framework's robustness in identifying transitions in oscillatory dynamics with pronounced nonlinearity.

\subsection{Lotka-Volterra Model}

The Lotka-Volterra model, commonly known as the predator-prey model, describes species interactions in an ecological system. Its key assumptions include closed population dynamics, a closed system with no migration, and a linear functional response in predator-prey interactions. The dynamics of a prey species $S$ and a predator species $W$ are governed by the following two-dimensional coupled differential equations:
\begin{equation}
\begin{cases}
\dfrac{{\rm d}S}{{\rm d}t} = S(\alpha - \beta W), \\[1mm]
\dfrac{{\rm d}W}{{\rm d}t} = - W(\gamma - \delta S),
\end{cases}
\end{equation}
where $\boldsymbol{x}(t) = (S(t), W(t))^\top$ and $\boldsymbol{\theta} = (\alpha, \beta, \gamma, \delta)$ in the traditional nonmixture ODE model \eqref{eq:3.5}. In this work, we employ the RAA-PINNs to jointly estimate the time-varying parameters and detect change points, illustrating the application to NDS-CPD.

We consider a Lotka-Volterra system with multiple time-varying parameters and multiple change points. A discrete state variable $r(t)$ with state space $\mathbb{I}$ is introduced to characterize the temporal variation of system parameters. Let $\mathbb{I} = \{1,2,3\}$ and $T=100$, and define
\begin{equation}
r(t) =
\begin{cases}
1, & 0 \le t < 20, \: 80 \le t \le 100, \\
2, & 20 \le t < 40, \: 60 \le t < 80, \\
3, & 40 \le t < 60.
\end{cases}
\end{equation}
Thus, the temporal evolution of $r(t)$ is $1 \to 2 \to 3 \to 2 \to 1$, and the corresponding piecewise parameters are
\begin{equation}
\boldsymbol{\theta}(t) =
\begin{cases}
(2,1,2,1), & r(t) = 1,\\
(4,2,3,4), & r(t) = 2,\\
(3,4,1,2), & r(t) = 3.
\end{cases}
\label{LV true value}
\end{equation}

The system output and sample paths are shown in Figure~\ref{fig:lotka_volterra}.

\begin{figure}[p]
    \centering
   \begin{minipage}[b]{1\linewidth}
        \centering
        \includegraphics[width=\linewidth]{figures/output_of_LV.pdf}
    \end{minipage}

    \vspace{0.1em}
    
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/sample_path_LV.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/LV_loss.pdf}
    \end{minipage}

    \vspace{0.1em}

    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/alpha.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/beta.pdf}
    \end{minipage}

    \vspace{0.1em}

     \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/gamma.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/delta.pdf}
    \end{minipage}

    \caption{Lotka-Volterra model. First row: trajectories of $(S(t), W(t))$ over $[0,100]$. Second row: sample path (left) and Stage~I candidate change-point intervals determined from the physical loss in the overlapping domain (right). Third and fourth rows: Stage~II results for parameter estimation and change-point localization.}
    \label{fig:lotka_volterra}
\end{figure}

\begin{table}[t]
\centering
\caption{Parameter estimation for the Lotka-Volterra model with time-varying parameters.}
\label{LV:parameter_estimation}
\small
\renewcommand{\arraystretch}{0.8}
\setlength{\tabcolsep}{6pt}

\begin{tabular}{w{c}{2cm} w{c}{2cm} w{c}{2cm} w{c}{3cm} w{c}{3cm}}

\toprule
\makecell[c]{Time} 
& \makecell[c]{Equation\\[-3pt] Coefficient} 
& \makecell[c]{True\\[-3pt] Value} 
& \makecell[c]{Parameter\\[-3pt] Estimation} 
& \makecell[c]{Squared Error\\[-3pt] of Parameter} \\
\midrule

\multirow{4}{*}{\makecell[c]{$[0,20]$}}
& $\alpha$ & 2  & 2.0238 & $5.664\times 10^{-4}$ \\
& $\beta$ & 1  & 0.9863 & $1.877\times 10^{-4}$ \\
& $\gamma$ & 2  & 1.9879 & $1.464\times 10^{-4}$ \\
& $\delta$ & 1  & 0.9878 & $1.488\times 10^{-4}$ \\

\midrule

\multirow{4}{*}{\makecell[c]{$[20,40]$}}
& $\alpha$ & 4  & 3.9912 & $7.774\times 10^{-5}$ \\
& $\beta$ & 2  & 1.9865 & $1.823\times 10^{-4}$ \\
& $\gamma$ & 3  & 3.0365 & $1.332\times 10^{-3}$ \\
& $\delta$ & 4  & 3.9876 & $1.538\times 10^{-4}$ \\

\midrule

\multirow{4}{*}{\makecell[c]{$[40,60]$}}
& $\alpha$ & 3  & 2.9878 & $1.488\times 10^{-4}$ \\
& $\beta$ & 4  & 3.9912 & $7.744\times 10^{-5}$ \\
& $\gamma$ & 1  & 0.9873 & $1.613\times 10^{-4}$ \\
& $\delta$ & 2  & 1.9684 & $9.985\times 10^{-4}$ \\

\midrule

\multirow{4}{*}{\makecell[c]{$[60,80]$}}
& $\alpha$ & 4  & 3.9865 & $1.823\times 10^{-4}$ \\
& $\beta$ & 2  & 1.9932 & $4.624\times 10^{-5}$ \\
& $\gamma$ & 3  & 2.9834 & $2.756\times 10^{-4}$ \\
& $\delta$ & 4  & 4.0534 & $2.852\times 10^{-3}$ \\

\midrule

\multirow{4}{*}{\makecell[c]{$[80,100]$}}
& $\alpha$ & 2  & 1.9845 & $2.403\times 10^{-4}$ \\
& $\beta$ & 1  & 0.9941 & $3.481\times 10^{-5}$ \\
& $\gamma$ & 2  & 2.0523 & $2.735\times 10^{-3}$ \\
& $\delta$ & 1  & 1.0376 & $1.414\times 10^{-3}$ \\

\bottomrule
\end{tabular}
\end{table}

In the Lotka-Volterra model, the time interval is $[0,100]$ with a window length of 2 and a step size of 1. This experiment validates the effectiveness and scalability of RAA-PINNs for multi-parameter coupled nonlinear systems. In each overlapping domain, all observation data are used to estimate the parameters $(\alpha, \beta, \gamma, \delta)$ independently. Elevated physical loss in domains containing change points is averaged over the last 100 training iterations to determine the Stage~I candidate intervals, which are $[19,21]$, $[39,41]$, $[59,61]$, and $[79,81]$.
In Stage~II, the candidate intervals are refined to jointly optimize the parameter values and change-point locations. The time-varying parameter estimates obtained using overlapping-domain RAA-PINNs and the corresponding change-point detection results are shown in Figure~\ref{fig:lotka_volterra}. Prediction errors, statistical inference results, and mean square errors for parameter recovery and change-point detection are reported in Tables~\ref{LV:parameter_estimation} and~\ref{tab:combined_change_points}.

Overall, the results of overlapping-domain RAA-PINNs agree well with the reference solution, successfully capturing all four change points. This demonstrates that RAA-PINNs can robustly handle multi-parameter coupled nonlinear systems, recovering simultaneous changes in interacting species.

\subsection{Lorenz System}

The Lorenz system is a canonical model in nonlinear dynamics, widely used to study chaotic behavior and complex dynamical phenomena. It was originally derived from a truncated Fourier expansion of the Navier-Stokes and heat equations describing fluid convection, and has played a fundamental role in revealing sensitive dependence on initial conditions and long-term unpredictability in deterministic systems. In this work, we employ the RAA-PINNs to jointly estimate time-varying parameters and detect change points, illustrating its application to NDS-CPD.

\begin{figure}[p]
    \centering
  \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth]{figures/output_of_lorentz1.png}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/sample_path_lorentz1.pdf}
    \end{minipage}

    \vspace{0.1em}
    
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/lorenz_loss.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/sigma.pdf}        
    \end{minipage}

    \vspace{0.1em}
    
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/r.pdf}
    \end{minipage}
     \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/b.pdf}
    \end{minipage}

    \caption{Lorenz model. Top row: trajectories of $(U(t), V(t), W(t))$ over $[0,20]$ (left) and the corresponding sample path (right). Second row: Stage~I candidate change-point intervals determined from the physical loss in the overlapping domain (left), and Stage~II results for parameter estimation and change-point localization (right). Other rows: Stage~II parameter estimation results.}
    \label{fig:lorenz}
\end{figure}

The system is described by the following three-dimensional coupled differential equations for the convective intensity $U$, the horizontal temperature gradient $V$ and the vertical temperature $W$:
\begin{equation}
\begin{cases}
\dfrac{{\rm d}U}{{\rm d}t} = \sigma (V - U), \\[1mm]
\dfrac{{\rm d}V}{{\rm d}t} = r U - V - U W, \\[1mm]
\dfrac{{\rm d}W}{{\rm d}t} = U V - b W,
\end{cases}
\end{equation}
where $\boldsymbol{x}(t) = (U(t), V(t), W(t))^\top$ and $\boldsymbol{\theta} = (\sigma, r, b)$ in the traditional nonmixture ODE model \eqref{eq:3.5}.

We consider a time-varying Lorenz system with multiple change points. A discrete state variable $r(t)$ with state space $\mathbb{I}$ is introduced to characterize the temporal evolution of system parameters. Let $\mathbb{I} = \{1,2,3\}$ and $T = 20$, and define
\begin{equation}
r(t) =
\begin{cases}
1, & 0 \le t < 8,\\
2, & 8 \le t < 16,\\
3, & 16 \le t \le 20.
\end{cases}
\end{equation}
Accordingly, the temporal evolution of $r(t)$ is $1 \to 2 \to 3$, and the piecewise parameter vector is
\begin{equation}
\boldsymbol{\theta}(t) =
\begin{cases}
[10, 28, 8/3], & r(t) = 1,\\
[12, 16, 10/3], & r(t) = 2,\\
[14, 20, 3], & r(t) = 3.
\end{cases}
\label{Lorentz true value}
\end{equation}
The system output and sample paths are shown in Figure~\ref{fig:lorenz}.

Given the sensitive dependence on initial conditions inherent in chaotic systems, trajectories diverge rapidly over longer time spans. Consequently, the simulation interval is restricted to $[0,20]$ to maintain numerical stability and allow RAA-PINNs to accurately recover the time-varying parameters and detect change points. The time interval is divided into 100 equal-length subintervals, with a window length of 0.2 and a step size of 0.1. In Stage~I, each window is independently trained for 30,000 iterations to estimate local constant parameters, and candidate change-point intervals are determined from elevated physical residuals. The Stage~I candidate intervals are $[7.9, 8.1]$ and $[15.9, 16.1]$, covering the true change points. In Stage~II, these intervals are refined to jointly optimize parameter values and change-point locations.

\begin{table}[t]
\centering
\caption{Parameter estimation and change-point detection of Lorenz system with time-varying parameters.}
\label{lorenz:parameter_estimation}
\small
\renewcommand{\arraystretch}{1}
\setlength{\tabcolsep}{6pt}

\begin{tabular}{w{c}{2cm} w{c}{2cm} w{c}{2cm} w{c}{3cm} w{c}{3cm}}

\toprule
\makecell[c]{Time} 
& \makecell[c]{Equation\\[-3pt] Coefficient} 
& \makecell[c]{True\\[-3pt] Value} 
& \makecell[c]{Parameter\\[-3pt] Estimation} 
& \makecell[c]{Squared Error\\[-3pt] of Parameter} \\
\midrule

\multirow{3}{*}{\makecell[c]{$[0,8]$}}
& $\sigma$ & 10  & 10.0238 & $5.664\times 10^{-4}$ \\
& $r$      & 28  & 27.9863 & $1.877\times 10^{-4}$ \\
& $b$      & 8/3  & 2.6877 & $4.424\times 10^{-4}$ \\

\midrule

\multirow{3}{*}{\makecell[c]{$[8,16]$}}
& $\sigma$ & 12  & 11.9912 & $7.774\times 10^{-5}$ \\
& $r$      & 16  & 15.9865 & $1.823\times 10^{-4}$ \\
& $b$      & 10/3 & 3.3787 & $2.058\times 10^{-3}$ \\

\midrule

\multirow{3}{*}{\makecell[c]{$[16,20]$}}
& $\sigma$ & 14  & 13.9878 & $1.488\times 10^{-4}$ \\
& $r$      & 20  & 19.9912 & $7.724\times 10^{-5}$ \\
& $b$      & 3   & 2.9873 & $1.613\times 10^{-4}$ \\

\bottomrule
\end{tabular}

\vspace{1.2em}

\caption{Estimates of change points for different numerical examples with time-varying parameters.}
\label{tab:combined_change_points}

\small
\renewcommand{\arraystretch}{1.0}
\setlength{\tabcolsep}{5pt}

\begin{tabular}{
w{c}{2.5cm}
w{c}{2cm}
w{c}{2cm}
w{c}{2.3cm}
w{c}{2.5cm}
w{c}{2.5cm}
}

\toprule
\makecell[c]{Numerical\\[-3pt] Example}
& \makecell[c]{Change point\\[-3pt] interval}
& \makecell[c]{True\\[-3pt] Value}
& \makecell[c]{Change point\\[-3pt] Estimation}
& \makecell[c]{Squared\\[-3pt] Error}
& \makecell[c]{MSE of\\[-3pt] $\mathbf{x}(t)$} \\
\midrule

% ===== Malthus =====
\multirow{1}{*}{\makecell[c]{Malthus}}
& $[39,41]$ & 40 & 40.0093 & $8.649\times10^{-5}$ & $3.854\times10^{-4}$ \\

\midrule

% ===== Logistic =====
\multirow{1}{*}{\makecell[c]{Logistic}}
& $[59,61]$ & 60 & 60.0037 & $1.369\times10^{-5}$ & $7.297\times10^{-4}$ \\

\midrule

% ===== Van der Pol =====
\multirow{2}{*}{\makecell[c]{Van der Pol}}
& $[39,41]$ & 40 & 40.0013 & $1.690\times10^{-6}$ & $4.372\times10^{-4}$ \\
& $[79,81]$ & 80 & 79.9987 & $1.690\times10^{-6}$ & $8.633\times10^{-5}$ \\

\midrule

% ===== Lotka-Volterra =====
\multirow{4}{*}{\makecell[c]{Lotka-Volterra}}
& $[19,21]$ & 20 & 20.0263 & $6.917\times10^{-4}$ & $2.538\times10^{-4}$ \\
& $[39,41]$ & 40 & 40.0139 & $1.932\times10^{-4}$ & $7.348\times10^{-4}$ \\
& $[59,61]$ & 60 & 60.0237 & $5.617\times10^{-4}$ & $3.283\times10^{-4}$ \\
& $[79,81]$ & 80 & 79.9897 & $1.061\times10^{-4}$ & $8.240\times10^{-5}$ \\

\midrule

% ===== Lorenz =====
\multirow{2}{*}{\makecell[c]{Lorenz}}
& $[7.9,8.1]$   & 8  & 8.0237  & $5.617\times10^{-4}$ & $3.184\times10^{-4}$ \\
& $[15.9,16.1]$ & 16 & 16.0128 & $1.638\times10^{-4}$ & $7.216\times10^{-4}$ \\

\bottomrule
\end{tabular}
\end{table}

\section{Parallel Overlapping Domain Strategy}
\label{sec:5}

Within each overlapping domain, all available observation data are used to estimate $\sigma$, $r$, and $b$ independently. The final time-varying parameter estimates and change-point locations obtained via RAA-PINNs are shown in Figure~\ref{fig:lorenz}. Prediction errors, statistical inference results, and mean square errors for parameter recovery and change-point detection are reported in Table~\ref{lorenz:parameter_estimation} and Table~\ref{tab:combined_change_points}. This demonstrates that RAA-PINNs can robustly recover parameters and accurately detect change points even in highly sensitive chaotic systems.

Overall, this example demonstrates that the framework can robustly recover parameters and accurately identify transitions even in highly sensitive chaotic systems, highlighting its applicability to complex chaotic dynamics.

For change-point detection in nonlinear dynamical systems with regime switching, the proposed RAA-PINNs framework combines residual-loss anomaly analysis with overlapping-domain training to achieve stable coarse localization and accurate local parameter inversion. However, the computational cost of overlapping-domain decomposition can become a major bottleneck in practical implementations, especially when the temporal resolution is high or the observation horizon is long. This issue is most pronounced in Stage~I, where independent PINNs must be trained on many overlapping subintervals in order to obtain reliable residual-loss statistics and identify candidate change-point regions. Since the number of subintervals grows approximately linearly with the temporal resolution and the coverage of the time domain, a serial implementation leads to an almost linear increase in total training time, which substantially limits the scalability of the method.

A key observation is that, in Stage~I, there are no interface coupling constraints between overlapping subintervals, and the corresponding training tasks are fully independent. Therefore, this stage has a natural parallel structure and can be directly mapped to multi-core CPUs, multi-GPU platforms, or distributed computing environments, leading to a substantial reduction in wall-clock time.

Let the temporal domain be $I=[0,T]$. In Stage~I, we construct a coarse partition
\begin{equation}
0=t_0 < t_1 < \cdots < t_K=T,
\end{equation}
and define $K$ overlapping subintervals with overlap width $\delta>0$ as
\begin{equation}
I_k = [t_{k-1}-\delta,\ t_k+\delta]\cap[0,T], \quad k=1,\ldots,K.
\end{equation}
On each $I_k$, we train an independent PINN $\boldsymbol{x}_{\phi_k}:I_k\rightarrow\mathbb{R}^n$ together with a local constant parameter $\boldsymbol{\theta}_k\in\Theta$ by minimizing the subinterval loss
\begin{equation}
\label{eq:subinterval_loss_parallel}
J_k(\phi_k,\boldsymbol{\theta}_k)
=
\sum_{t_j\in S_d^{(k)}} w_{j,k}^d \bigl\|\mathcal{R}_{\mathrm{data}}[\boldsymbol{x}_{\phi_k},\boldsymbol{\theta}_k](t_j)\bigr\|_2^2
+
\lambda \sum_{s_i\in S_{\mathrm{int}}^{(k)}} w_{i,k}^r \bigl\|\mathcal{R}_{\mathrm{int}}[\boldsymbol{x}_{\phi_k},\boldsymbol{\theta}_k](s_i)\bigr\|_p^p,
\end{equation}
where $S_d^{(k)}\subset I_k$ denotes the measurement set, $S_{\mathrm{int}}^{(k)}\subset I_k$ denotes the interior collocation set, and $\lambda>0$ balances the data mismatch and physics residual.

Crucially, the optimization problems $\{J_k\}_{k=1}^K$ are mutually independent. The absence of cross-subinterval coupling enables direct parallelization at the subinterval level, with each pair $(\phi_k,\boldsymbol{\theta}_k)$ optimized on a separate computational unit.

Let $t_{\mathrm{sub}}$ denote the average training time for one PINN on a single Stage~I subinterval, and let $K$ be the number of overlapping subintervals. Then the total runtime of serial Stage~I, denoted by $T_s^{(\mathrm{I})}$, can be approximated as
\begin{equation}
T_s^{(\mathrm{I})} = K\,t_{\mathrm{sub}}+c_1,
\end{equation}
where $c_1$ collects additional overhead that is typically much smaller than $K\,t_{\mathrm{sub}}$ and therefore does not affect the overall scaling behavior. Given load-balancing effects and communication overhead, the runtime $T_p^{(\mathrm{I})}$ with $P$ parallel workers can be approximated by
\begin{equation}
T_p^{(\mathrm{I})} = \left\lceil \frac{K}{P}\right\rceil t_{\mathrm{sub}}+c_2,
\end{equation}
where $c_2$ denotes parallelization overhead and is typically much smaller than $\left\lceil K / P \right\rceil\,t_{\mathrm{sub}}$. Hence, the theoretical speedup is given by
\begin{equation}
\mathcal{S}^{(\mathrm{I})}
=
T_s^{(\mathrm{I})}/T_p^{(\mathrm{I})}.
\end{equation}
When $K\gg P$, we obtain $\mathcal{S}^{(\mathrm{I})}\approx P$, indicating near-linear scaling.

Moreover, Stage~II is carried out only on a narrow candidate interval and typically requires training one or only a few local PINNs. As a result, the total runtime of the two-stage RAA-PINNs framework is dominated by Stage~I. The total runtime under serial and parallel implementations can therefore be written as
\begin{equation}
T_s
=
T_s^{(\mathrm{I})} + T^{(\mathrm{II})},
\quad
T_p
=
T_p^{(\mathrm{I})} + T^{(\mathrm{II})}.
\end{equation}

In our experiments, each GPU with 24\,GB of memory can execute 16 tasks concurrently. Using 8 GPUs yields a total of $8\times 16=128$ concurrent tasks. We evaluate the computational benefit of this parallel strategy on three representative nonlinear dynamical systems with discontinuous parameters: the Van der Pol oscillator, the Lotka-Volterra model, and the Lorenz system. These examples cover oscillatory, coupled population, and chaotic dynamics, respectively, and therefore provide a representative testbed for assessing the scalability of RAA-PINNs. The results are presented in Table~\ref{tab:time_comparison_template}.

\begin{table}[t]
\centering
\caption{Runtime comparison of the proposed framework under serial and parallel implementations. Here $P$ denotes the number of parallel workers, $\mathcal{S}=T_s/T_p$ is the speedup, and $\mathcal{E}=\mathcal{S}/P$ is the parallel efficiency.}
\label{tab:time_comparison_template}
\small
\renewcommand{\arraystretch}{1.0}
\setlength{\tabcolsep}{6pt}

\begin{tabular}{w{c}{1.8cm} w{c}{1.6cm} w{c}{1.6cm} w{c}{1.6cm} w{c}{1.6cm} w{c}{1.6cm} w{c}{1.6cm} w{c}{1.6cm}}

\toprule
\makecell[c]{Example} 
& \makecell[c]{Stage} 
& \makecell[c]{$K$} 
& \makecell[c]{$P$} 
& \makecell[c]{$T_s(s)$} 
& \makecell[c]{$T_p(s)$} 
& \makecell[c]{$\mathcal{S}$}
& \makecell[c]{$\mathcal{E}$} \\
\midrule

\multirow{3}{*}{\makecell[c]{Van der Pol}}
& $\text{I}$  & 100 & 128 & 53625.7 & 425.1 & 126.152 & 0.986 \\
& $\text{II}$ & 2   & 128 & 167.9   & 92.6  & 1.811   & 0.014 \\
& Total       &     & 128 & 53793.6 & 517.7 & 103.915 & 0.812 \\

\midrule

\multirow{3}{*}{\makecell[c]{Lotka-Volterra}}
& $\text{I}$  & 100 & 128 & 55554.8 & 594.5 & 93.465 & 0.730 \\
& $\text{II}$ & 4   & 128 & 401.2   & 108.2 & 3.771  & 0.029 \\
& Total       &     & 128 & 55956.0 & 702.7 & 79.525 & 0.621 \\

\midrule

\multirow{3}{*}{\makecell[c]{Lorenz}}
& $\text{I}$  & 100 & 128 & 72812.3 & 718.0 & 101.339 & 0.792 \\
& $\text{II}$ & 2   & 128 & 252.6   & 119.5 & 2.141  & 0.016 \\
& Total       &     & 128 & 73064.9 & 837.5 & 87.288 & 0.682 \\

\bottomrule
\end{tabular}
\end{table}

Notably, the parallel strategy changes only the scheduling of independent subinterval optimization tasks. It does not alter the mathematical form of the subinterval losses or the Stage~II refinement procedure. Therefore, the parallel and serial implementations produce consistent change-point localization and parameter reconstruction results, while the wall-clock time is substantially reduced. This confirms that the proposed parallel overlapping-domain strategy improves the computational scalability of RAA-PINNs without sacrificing inversion accuracy.

\section{Comparative Experiment}\label{sec6}

In this section, we compare the proposed method with both traditional statistical baselines and existing neural-network-based approaches. The goal is to evaluate its performance on two core tasks in nonlinear dynamical systems with regime switching: parameter estimation and change-point localization. The comparative study is carried out on representative systems to highlight the differences in modeling strategy, reconstruction accuracy, and localization precision.

\subsection{Traditional Statistical Method}
For ordinary differential equation systems with discontinuous parameters, we adopt a two-stage statistical pipeline as the baseline for comparison. Specifically, the baseline combines adaptive gradient matching (AGM)\cite{dondelinger2013ode} for ODE parameter inference with Pruned Exact Linear Time (PELT)\cite{killick2012optimal} for penalized change-point detection, hereafter referred to as AGM-PELT. Under this baseline, parameter estimation is carried out within a probabilistic inference framework using AGM. In this approach, Gaussian processes are used to model the latent system trajectory, while the governing ODE is incorporated as a soft constraint rather than being enforced exactly. The resulting joint inference problem can be formulated as
\begin{equation}
    (\hat{\boldsymbol{x}}, \hat{\boldsymbol{\theta}})
=
\arg\max_{\boldsymbol{x},\boldsymbol{\theta}}
\;
p(y \mid \boldsymbol{x})\,
p\!\left(\dot{\boldsymbol{x}} \mid f(\boldsymbol{x};\boldsymbol{\theta})\right),
\end{equation}
which yields a time-dependent parameter sequence $\{\boldsymbol{\theta}_t\}_{t=1}^{T}$. Within this statistical formulation, the parameters are treated as stochastic quantities, and the governing equations are incorporated through probabilistic consistency between the inferred trajectory and the ODE dynamics.


\begin{figure}[t]
    \centering
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/duibi_alpha.pdf}
    \end{minipage}%
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/duibi_beta.pdf}
    \end{minipage}

    \vspace{0.1em}

    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/duibi_gamma.pdf}
    \end{minipage}%
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=0.8cm 0.1cm 0.8cm 0.1cm,clip]{figures/duibi_delta.pdf}
    \end{minipage}
    \caption{Learned parameter trajectories for the Lotka-Volterra model obtained by different methods, where the parameters are $\boldsymbol{\theta}=(\alpha,\beta,\gamma,\delta)$.}
    \label{fig:duibi}
\end{figure}

Given the estimated parameter sequence $ \{\boldsymbol{\theta}_t\} $, change-point detection is then formulated as a penalized global segmentation problem:
\begin{equation}
    \{\tau_i\}
=
\arg\min_{m,\{\tau_i\}}
\left\{
\sum_{i=1}^{m+1}
\mathcal{C}\!\left(
\{\boldsymbol{\theta}_t\}_{t=\tau_{i-1}}^{\tau_i}
\right)
+
\psi m
\right\},
\end{equation}
where $ \mathcal{C}(\cdot) $ denotes a segment-wise cost function and $ \psi $ is a penalty parameter controlling the number of detected change points. This optimization is solved using the PELT algorithm, which combines dynamic programming with pruning to obtain an exact solution for the chosen penalized cost. Under suitable conditions, its expected computational cost can scale linearly with the sequence length. Accordingly, the detection performance depends on both the choice of the segment-wise cost function and the specification of the penalty parameter.

In contrast, the proposed method embeds parameter inference directly into a physics-informed inverse framework. Instead of first estimating a time-varying parameter trajectory and then segmenting it, the governing dynamics are enforced explicitly over multiple overlapping subintervals, so that parameter estimation remains tightly coupled with the underlying dynamical system. This design reduces the potential mismatch between statistically smoothed trajectories and physically admissible dynamics.

The proposed two-stage strategy adopts a different perspective on change-point detection. In Stage~I, neural networks trained on overlapping subintervals exhibit clear residual-loss anomalies in regions where parameter discontinuities occur, thereby naturally identifying candidate change-point intervals. Then in Stage~II, refined local modeling is carried out only within these intervals to jointly infer the piecewise parameters and the change-point locations. In this way, change points are not obtained through explicit segmentation of a pre-estimated parameter sequence, but instead emerge from local breakdowns of physical consistency. Comparative experiments between this statistical baseline and the proposed method are conducted on the Lotka-Volterra system, and the results are reported in Figure~\ref{fig:duibi} and Table~\ref{tab:lv_comparison_methods}.

Overall, the results show that the proposed method provides a more faithful reconstruction of discontinuous parameters than the AGM-PELT baseline. For all four coefficients, the recovered trajectories are closer to the reference piecewise-constant structure, exhibit smaller within-regime dispersion, and display sharper transitions at the discontinuities. In contrast, the AGM-PELT baseline shows noticeable scatter around the true parameter levels, and its representation of regime-wise dynamics is less accurate. This qualitative difference is also supported by the mean squared errors reported in Table~\ref{tab:lv_comparison_methods}, where the proposed method consistently achieves lower errors than the baseline.

\subsection{Existing Neural Network Method}

For ordinary differential equation systems with jump parameters, the PINNs combined with statistical learning algorithm named expectation-maximization for Gaussian mixture models (PINNs-EM-GMM) framework is a recently proposed hybrid approach for joint parameter estimation and change-point detection~\cite{zhang2025data}. It combines PINNs-based parameter inversion with statistical mechanism identification. Let the system state be observed as $\{\boldsymbol{x}(t_i)\}_{i=1}^N$ and governed by the ODE as
\begin{equation}
\dot{\boldsymbol{x}}(t) = f\big(t,\boldsymbol{x}(t); \boldsymbol{\theta}(t)\big), 
\quad 
\boldsymbol{\theta}(t) \in \mathbb{R}^d,
\end{equation}
where $\boldsymbol{\theta}(t)$ represents the time-varying parameter vector.

The PINNs-EM-GMM framework consists of two stages. In the first stage, sliding-window PINNs are employed to reconstruct the state function $\boldsymbol{x}_\phi(t)$ and the parameter function $\boldsymbol{\theta}_\xi(t)$ locally over each time window $[t_s,t_e]$ by minimizing the composite loss
\begin{equation}
\mathcal{J}
=
\sum_{t_i \in \mathcal{T}_{\mathrm{obs}}}
\|\boldsymbol{x}_\phi(t_i) - \boldsymbol{x}(t_i)\|_2^2
+
\lambda
\sum_{t_j \in \mathcal{T}_{\mathrm{res}}}
\bigl\|
\dot{\boldsymbol{x}}_\phi(t_j)
-
f\bigl(t_j,\boldsymbol{x}_\phi(t_j);\boldsymbol{\theta}_\xi(t_j)\bigr)
\bigr\|_2^2,
\end{equation}
where the first term penalizes data mismatch and the second enforces physical consistency, with $\lambda>0$ controlling the weight of the residual. By leveraging overlapping windows and adaptive residual weighting, the network can capture rapid changes near transition points while mitigating cross-regime compromise, yielding a smooth continuous parameter trajectory $\widehat{\boldsymbol{\theta}}(t)$.

\begin{figure}[p]
    \centering
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=1cm 0.1cm 0.8cm 0.1cm,clip]{figures/EM_duibi_alpha.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=1cm 0.1cm 0.8cm 0.1cm,clip]{figures/EM_duibi_beta.pdf}
    \end{minipage}

    \vspace{0.1em}

    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=1cm 0.1cm 0.8cm 0.1cm,clip]{figures/EM_duibi_gamma.pdf}
    \end{minipage}
    \begin{minipage}[b]{0.495\linewidth}
        \centering
        \includegraphics[width=\linewidth,trim=1cm 0.1cm 0.8cm 0.1cm,clip]{figures/EM_duibi_delta.pdf}
    \end{minipage}

        \vspace{0.1em}

\begin{minipage}[b]{1\linewidth}
        \centering
        \includegraphics[width=\linewidth]{figures/LV_change_probability.pdf}
    \end{minipage}

\caption{First and second rows: learned parameter trajectories $\boldsymbol{\theta}=(\alpha,\beta,\gamma,\delta)$ of the Lotka-Volterra model obtained using different PINNs methods. 
Third row: change-point detection results based on the EM-GMM approach.}
\label{EM duibi}
\end{figure}

In the second stage, mechanism discretization and change-point detection are performed. The continuous trajectory is treated as a sample sequence generated from a finite set of latent regimes. For each parameter component $\widehat{\theta}_i(t)$, a $K$-component Gaussian mixture model is employed to characterize its distribution:
\begin{equation}
p\bigl(\widehat{\theta}_i(t)\bigr)
=
\sum_{k=1}^{K}
\eta_{ik}\,
\mathcal{N}\!\bigl(\widehat{\theta}_i(t)\mid \mu_{ik},\sigma_{ik}^{2}\bigr),
\end{equation}
where $\eta_{ik}$, $\mu_{ik}$, and $\sigma_{ik}^{2}$ denote the mixture weight, mean, and variance of the $k$-th cluster, respectively. The EM algorithm estimates these parameters and computes the posterior cluster probability for each time point as
\begin{equation}
\gamma_{ik}(t)
=
P\bigl(z_i(t)=k \mid \widehat{\theta}_i(t)\bigr).
\end{equation}

A change-point probability is then constructed via a three-point local consistency measure
\begin{equation}
p_i(t)
=
1-\sum_{k=1}^{K}
\gamma_{ik}(t-\Delta t)\,
\gamma_{ik}(t)\,
\gamma_{ik}(t+\Delta t),
\end{equation}
and the probabilities across all parameters are averaged to obtain a combined change-point probability
\begin{equation}
p(t)
=
\frac{1}{d}\sum_{i=1}^{d} p_i(t).
\end{equation}

The top $N_{\mathrm{cp}}$ change points are selected from the peaks of $p(t)$, and the corresponding credible intervals are formed as
\begin{equation}
\mathcal{I}_j
=
\bigl[\min_i \widehat{\tau}_{ij},\; \max_i \widehat{\tau}_{ij}\bigr].
\end{equation}

This framework integrates continuous parameter inversion, statistical regime discretization, and the posterior-based change-point detection into a unified pipeline. As a result, it provides an interpretable statistical representation of both parameter evolution and mechanism transitions, and can exhibit robustness in noisy settings.

The comparative results show that the PINNs-EM-GMM method achieves high accuracy in reconstructing parameter trajectories. As shown in Figure~\ref{EM duibi}, it effectively captures the piecewise evolution of the system parameters effectively. In addition, Table~\ref{tab:lv_comparison_methods} reports the mean squared errors of the parameters $(\alpha,\beta,\gamma,\delta)$, indicating accurate parameter estimation across all four dimensions. Figure~\ref{EM duibi} also presents the change-point probability together with the true and predicted change-point locations. Pronounced probability peaks appear near the true change points, demonstrating the method’s ability to identify candidate transition regions reliably. The detected change-point intervals, namely $[18.6093, 21.2106]$, $[38.8694, 41.1029]$, $[59.5799, 61.2806]$, and $[78.8894, 81.3907]$, all contain the true change-point locations, indicating strong interval-level localization performance.

However, because it relies on statistical discretization and local posterior-consistency measures, the PINNs-EM-GMM framework intrinsically produces interval estimates rather than direct point estimates of change-point locations. By contrast, the proposed two-stage method first identifies candidate transition regions through residual-loss anomalies observed in overlapping subintervals, and then introduces a differentiable parameterization of the change point within each candidate region so that the transition location and the piecewise parameters can be optimized jointly under a unified physics-informed objective. Consequently, while maintaining comparable accuracy in parameter estimation, the proposed method further improves change-point localization by refining interval-level detection into direct pointwise estimation.



\begin{table}[t]
\centering
\caption{Comparison of squared parameter estimation errors for the Lotka-Volterra model with time-varying parameters.}
\label{tab:lv_comparison_methods}
\small
\renewcommand{\arraystretch}{1.05}
\setlength{\tabcolsep}{7pt}

\begin{tabular}{
w{c}{2.2cm}
w{c}{1.8cm}
w{c}{2.2cm}
w{c}{2.2cm}
w{c}{2.2cm}
w{c}{2.2cm}
}
\toprule
\makecell[c]{Method}
& \makecell[c]{Time}
& \makecell[c]{Squared Error\\[-3pt] of $\alpha$}
& \makecell[c]{Squared Error\\[-3pt] of $\beta$}
& \makecell[c]{Squared Error\\[-3pt] of $\gamma$}
& \makecell[c]{Squared Error\\[-3pt] of $\delta$} \\
\midrule

\multirow{5}{*}{\makecell[c]{RAA-PINNs}}
& $[0,20]$   & $5.664\times 10^{-4}$ & $1.877\times 10^{-4}$ & $1.464\times 10^{-4}$ & $1.488\times 10^{-4}$ \\
& $[20,40]$  & $7.774\times 10^{-5}$ & $1.823\times 10^{-4}$ & $1.332\times 10^{-3}$ & $1.538\times 10^{-4}$ \\
& $[40,60]$  & $1.488\times 10^{-4}$ & $7.744\times 10^{-5}$ & $1.613\times 10^{-4}$ & $9.985\times 10^{-4}$ \\
& $[60,80]$  & $1.823\times 10^{-4}$ & $4.624\times 10^{-5}$ & $2.756\times 10^{-4}$ & $2.852\times 10^{-3}$ \\
& $[80,100]$ & $2.403\times 10^{-4}$ & $3.481\times 10^{-5}$ & $2.735\times 10^{-3}$ & $1.414\times 10^{-3}$ \\
\midrule

\multirow{5}{*}{\makecell[c]{AGM-PELT}}
& $[0,20]$   & $7.079\times 10^{-2}$ & $2.778\times 10^{-2}$ & $2.039\times 10^{-3}$ & $1.993\times 10^{-2}$ \\
& $[20,40]$  & $1.042\times 10^{-1}$ & $2.522\times 10^{-2}$ & $1.476\times 10^{-1}$ & $2.288\times 10^{-2}$ \\
& $[40,60]$  & $1.818\times 10^{-2}$ & $1.014\times 10^{-3}$ & $2.053\times 10^{-2}$ & $1.215\times 10^{-1}$ \\
& $[60,80]$  & $2.338\times 10^{-2}$ & $6.539\times 10^{-2}$ & $3.252\times 10^{-2}$ & $3.724\times 10^{-3}$ \\
& $[80,100]$ & $2.706\times 10^{-1}$ & $5.150\times 10^{-2}$ & $4.065\times 10^{-1}$ & $2.013\times 10^{-1}$ \\
\midrule

\multirow{5}{*}{\makecell[c]{PINNs-EM-GMM}}
& $[0,20]$   & $4.885\times 10^{-3}$ & $1.619\times 10^{-3}$ & $1.205\times 10^{-2}$ & $1.706\times 10^{-3}$ \\
& $[20,40]$  & $8.808\times 10^{-3}$ & $1.613\times 10^{-3}$ & $1.162\times 10^{-4}$ & $1.343\times 10^{-3}$ \\
& $[40,60]$  & $1.555\times 10^{-4}$ & $6.627\times 10^{-4}$ & $1.479\times 10^{-4}$ & $9.451\times 10^{-4}$ \\
& $[60,80]$  & $1.890\times 10^{-4}$ & $3.785\times 10^{-3}$ & $2.875\times 10^{-4}$ & $2.476\times 10^{-3}$ \\
& $[80,100]$ & $2.215\times 10^{-4}$ & $2.921\times 10^{-4}$ & $2.937\times 10^{-3}$ & $1.380\times 10^{-3}$ \\
\bottomrule
\end{tabular}
\end{table}


\section{Conclusion and Discussion}\label{sec7}
This work presents a residual-loss anomaly-based inverse framework for change-point detection and parameter identification in nonlinear dynamical systems with regime switching. The core idea is to analyze the anomalous behavior of the physics-based residual loss, which is highly sensitive to local inconsistencies caused by parameter discontinuities. Exploiting this mechanism allows the identification of candidate change-point intervals and the recovery of piecewise system parameters. The method proceeds in two stages: in the first stage, overlapping subintervals are analyzed, where parameter changes induce localized violations of physical consistency, enabling effective localization of candidate intervals. In the second stage, these intervals are refined to jointly infer the change-point locations and the corresponding parameters. Systematic experiments on representative systems, including simple growth models, nonlinear oscillators, coupled multi-parameter systems, and chaotic systems, demonstrate that this approach accurately identifies change points, reconstructs parameters, and captures latent state transitions across a wide range of nonlinear dynamics. Each example highlights a specific capability, abrupt transitions in simple growth, nonlinear saturation effects, self-excited oscillatory dynamics, coupled multi-parameter interactions, and robustness under chaos with strong sensitivity to initial conditions.

Compared with traditional statistical approaches, such as Gaussian-process-based methods, this framework provides greater modeling flexibility and physical consistency for strongly nonlinear systems with pronounced parameter discontinuities. It maintains robust performance under limited observational data, accurately recovers parameters, and reliably characterizes states near change points, without requiring prior knowledge of transition times. While supported by theoretical analysis and numerical evidence, further studies of its generalization under noisy observations, model misspecification, and uncertainty quantification would enhance its reliability. Future extensions may include high-dimensional coupled systems, stochastic dynamics, and partial differential equation models with regime switching. Potential applications span practical state monitoring and transition analysis in real-world systems, such as modeling the growth dynamics of hemangiomas or analyzing phase-wise vascular aging from time-series observations derived via computer vision, highlighting the framework’s broad applicability in nonlinear dynamical system identification and change-point analysis.



%\section*{Appendix}

\setstretch{1}
\bibliography{reference1}
%\section*{References}

%\begin{thebibliography}{99}
%\end{thebibliography}

\end{document}
