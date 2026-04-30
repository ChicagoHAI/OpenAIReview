\documentclass[11pt,a4paper]{article}

\input{settings/header.tex}

\excludefalse
\usepackage{booktabs}

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

\newcommand{\ICNN}{\operatorname{ICNN}}
\newcommand{\HyCNN}{\operatorname{HyCNN}}
\newcommand{\ReLU}{\operatorname{ReLU}}

\renewcommand\com[1]{{\textcolor{red}{[#1]}}}
\renewcommand\sh[1]{{\textcolor{red}{[SH: #1]}}}
\newcommand\is[1]{{\textcolor{cyan}{[IK: #1]}}}
\newcommand\ik[1]{{\textcolor{cyan}{[IK: #1]}}}
\newcommand\jsh[1]{{\textcolor{violet}{[JSH: #1]}}}

\DeclareMathOperator*{\argmax}{argmax}
\DeclareMathOperator*{\argmin}{argmin}
\DeclareMathOperator{\maxs}{max^\sigma}

\begin{document}
%
%
\title{\textbf{Hyper Input Convex Neural Networks for Shape Constrained Learning and Optimal Transport}}
\input{settings/meta.tex}
\newcommand{\parabold}[1]{\subsection{#1}}

%
\section{Introduction}\label{sec:introduction}

This paper introduces a novel neural network architecture, called Hyper Input Convex Neural Network (HyCNN)%
, which is $(i)$ always convex in its inputs, $(ii)$ explicitly designed to harness depth for approximation, and $(iii)$ outperforms alternative procedures in terms of predictive power when trained at depth for large data sets, see \Cref{fig:HyCNN}. 

\parabold{Shape constrained learning}
Among shape constraints, \emph{convexity in the input} is favorable for multiple reasons.
First, convexity goes beyond being a convenient inductive bias as it is intrinsic to several core problems.
In optimal transport (OT) with squared Euclidean costs, Brenier's theorem asserts that the OT map between absolutely continuous probability measures with finite second moment is given by the gradient of a convex potential \citep{brenier1991polar,villani2008optimal,peyre2019computational}. Hence, learning an OT maps is naturally linked to learning a convex function \citep{taghvaei20192,makkuva2020optimal,bunne2023learning}. In invertible generative modeling, gradients of (strongly) convex potentials yield monotone diffeomorphisms that serve to define normalizing flows \citep{rezende2015variational,huang2020convex}. 
Convex models also arise in optimal control, where convexity is used to ensure planning computational feasibility while using expressive learned dynamics or cost surrogates \citep{chen2018optimal}.


\begin{figure}[t!]
%
  \begin{center}
    \centerline{\includegraphics[width=\textwidth]{HyCNN_intro_2.pdf}}
    \caption{{Input convex neural networks (ICNNs) versus Hyper Input Convex Neural Networks (HyCNNs).} \textbf{(a)} Depiction of generic input convex network architecture. ICNN blocks comprise one lane, whereas Hyper ICNN (HyCNN) blocks involve two lanes of matrix operations. \textbf{(b)} Averaged Empirical MSE over 10 repetitions with $(10\%-90\%)$ confidence bands for learning the function $f_0(x) = \|\bx\|_2^2$ on $\RR^d$ with $d = 50$ based on $n = 5,000$ samples of the form $(\bX_i, Y_i)_{i\in [n]}$ with $\bX_i \sim \mathrm{Unif}[-1,1]^d$ and $Y_i = f_0(\bX_i) + \epsilon_i$ with $\epsilon_i \sim \mathcal{N}(0,1)$. Two network architectures are used, ICNN \citep{amos2017input} and HyCNN (ours)  where the label $(m \times L)$ indicates width $m$ and depth $L$ of the network.  \textbf{(c)} Rotational profiles $t \mapsto f(t \bv_i)$ of ground truth (dashed) and learned networks with best MSE performance within network class, for $100$ randomly drawn directions $\bv_i \sim \mathrm{Unif}(\SS^{d-1})$.}
    \label{fig:HyCNN}
 \end{center}
\end{figure}

Second, for a real-valued function $f(\cdot)$ that is convex and coercive, operations such as $$\arg\min_{\bx\in \RR^d} f(\bx)$$ become tractable via convex optimization, and gradients/subgradients are globally well-behaved. As such, network architectures that are convex in the input are natural candidates for learning energy functions, which are ubiquitous in machine learning and statistics, e.g., to devise better optimization heuristics and parameterizations for data-driven mirror descent \citep{tan2023data}, to design convolutional networks which are more robust to noise \citep{sivaprasad2021curious}, and to enforce related shape-specific properties on level sets  \citep{nesterov2022learning}. 


%
Third, convexity lies at the heart of classical shape-restricted statistics problems such as convex regression \citep{seijo2011convex,hannah2013multivariate,guntuboyina2015global,balazs2015near} and log-concave density estimation \citep{samworth2018recent}. Convex energy parameterizations have recently also been used to scale such problems with deep learning infrastructure \citep{lin2023falcon} and interact naturally with score-based learning objectives \citep{hyvarinen2005estimation,song2021score}, see \cite{feng2024optimal} for a recent example of shape-constrained score-based regression. 

Despite these motivations, the performance of existing convex neural architectures in small to moderate dimensions is often only comparable to that of unconstrained (multi-layer perceptron, MLP) networks, even when convexity is known to hold, see \Cref{app:interpolation} of the supplementary material, in particular for deeper architectures. 
%
A potential reason is that most input-convex constructions are not easy to train at depth, and thus fail to leverage the approximation benefits of deeper architectures. Moreover, as we show in \Cref{sec:approximation}, ICNNs are provably inefficient at approximating quadratic functions, which are fundamental building blocks for convex functions. Our architecture aims to resolve both issues. 
%

\parabold{Neural networks which are convex in the input}\label{sec:related_work_icnns} 
\emph{Input convex neural networks} (ICNNs)  \citep{amos2017input} are the 
dominant architecture to guarantee convexity with respect to the inputs. A principled initialization strategy improves the practical performance of ICNNs \citep{hoedt2023principled}. 
Modifications to ICNNs have been proposed to improve their expressiveness, e.g., by using bilinear positive definite skip connections from the input \citep{bunne2023learning}.

%

Based on the representation of convex piecewise-affine functions as maxima of affine forms, alternative input convex network constructions focus on maxout units \citep{goodfellow2013maxout}. This includes
groupwise maximum networks \citep{warin2023groupmax} for convex approximation and input convex Kolmogorov--Arnold networks (KANs) \citep{warin2024p1,deschatre2025input,thakolkaran2025can}. Despite the conceptual appeal of these architectures, they have not been able to consistently outperform ICNNs in practice, and their quantitative approximation properties are not well understood.  

%

%
%

\parabold{Contributions} 
We introduce \emph{Hyper Input Convex Neural Networks (HyCNNs)}, a novel shape-constrained architecture designed to approximate convex functions while leveraging depth and remaining trainable at scale.
At a high level, a HyCNN combines two ideas:
$(i)$ parameter constraints as in ICNNs to ensure convexity, and $(ii)$ using maxout units to allow each layer to refine the piecewise-affine structure of the approximation. %
With appropriate nonnegativity constraints on hidden-to-hidden weights, HyCNNs are convex by construction (Proposition~\ref{prop:HyCNN_convexity}), include standard ReLU ICNNs as a special case, and inherit known universal approximation guarantees for convex functions \citep{amos2017input,chen2018optimal}. We also provide a principled initialization strategy for HyCNNs that ensures stable signal propagation across layers at initialization, which is crucial for training deep networks. 
%
%

Our core technical insight is that the modified convex unit fundamentally changes the \emph{depth--expressiveness trade-off}.
Specifically, compared to a classical ICNN layer, each HyCNN layer can \emph{double} the number of affine pieces in the induced piecewise-affine approximation, leading to an exponential-in-depth refinement mechanism. We formalize this by proving that constant-width HyCNNs approximate the quadratic function on $[0,1]$ with uniform error decaying as $O(2^{-2L})$ in the number of layers $L$ (Theorem~\ref{thm:quadratic_approximation}).
In contrast, ReLU-based ICNNs in one dimension remain convex and piecewise-affine, but their number of linear pieces grows only linearly with depth (\Cref{prop:piecewise_linear_icnn}), which yields a polynomial lower bound on the best achievable uniform error for $x\mapsto x^2$ (Theorem~\ref{thm:lowerBoundPiecewiseLinear}).
This gap provides a concrete explanation for why ``making ICNNs deeper'' often fails to deliver commensurate gains in practice.

We then apply HyCNNs to learn high-dimensional OT maps, where we outperform
multiple variants of ICNNs and  the Monge Gap MLP estimator in terms of predictive performance. In addition, we demonstrate the versatility of HyCNNs by applying them to various synthetic regression problems, demonstrating superior performance over existing convex neural architectures. 

%
%

\parabold{Paper organization} 
Section~\ref{sec:HyCNNs} introduces the HyCNN architecture, establishes convexity, and discusses initialization and training rules. 
Section~\ref{sec:approximation} compares the approximation properties of HyCNNs and ICNNs. 
Section \ref{sec:applications} presents applications of HyCNNs to optimal transport map estimation. Section \ref{sec:experiments} provides empirical results. The supplementary material  contains additional results to our approximation theory, omitted proofs, and additional experiments.

%

%

\section{HyCNNs: Hyper Input Convex Neural Networks}\label{sec:HyCNNs}

\parabold{Architecture}
Our architecture of the HyCNN takes inspiration from maxout networks \citep{goodfellow2013maxout} and input convex neural networks \citep{amos2017input}. To introduce HyCNNs, we first recall the construction of ICNNs. Formally, an ICNN 
%
takes a $d$-dimensional input $\bx \in \RR^d$ and outputs a real number; it exhibits $L\in \NN$ hidden layers and the number of hidden neurons per layer is characterized by $(d_1, \dots, d_L)\in \NN^L$. The output of each layer and the function is given by the following equations for $\ell = 0, \dots, L-1$ (see \Cref{fig:HyCNN}(a)):
\begin{align}\label{eq:ICNN}
    \   \operatorname{ICNN}(\bx) := \bz_{L+1} \coloneqq V_{L}\bz_L + W_L \bx + \bb_L, \qquad \bz_{\ell+1} &:= \sigma(V_\ell \bz_{\ell} + W_{\ell} \bx + \bb_{\ell}),
\end{align}
where $\bz_0 \coloneqq \mathbf{0}_d$ and $\bz_\ell$ is given by the layerwise activation function $\sigma\colon \RR \to \RR$ applied componentwise, with parameters 
%
consisting of weight matrices and biases. 
To ensure that $f$ is convex in $\bx$,
the activation function $\sigma$ is convex and non-decreasing (e.g., ReLU),
the weight-matrices $\{V_\ell\}_{\ell=0}^L$ are constrained to be non-negative, while $\{W_\ell\}_{\ell=0}^L$ and $\{\bb_\ell\}_{\ell=0}^L$ are unconstrained \citep[Proposition 1]{amos2017input}.

For the HyCNN architecture, we modify the layerwise construction of ICNNs by introducing an additional lane of matrix operations. Concretely, a HyCNN 
%
with $L$ layers and $(d_1, \dots, d_L)$ hidden neurons per layer is given by the following equations for $\ell = 0, \dots, L-1$:
\begin{align}\label{eq:HyCNN}
\operatorname{HyCNN}(\bx) := \bz_{L+1} = V_{L}\bz_L + W_L \bx + \bb_L, \qquad     \bz_{\ell+1} &:= \overline\sigma\left((V_\ell^{k} \bz_{\ell} + W_{\ell}^{k} \bx + \bb_{\ell}^{k})_{k\in \{1,2\}}\right), 
\end{align}
where $\bz_0\coloneqq \mathbf{0}_d$ and $\overline \sigma$ represents the \emph{(gating) activation function} $\overline \sigma\colon \RR^2 \to \RR$ that is convex and componentwise non-decreasing, and the notation $\overline\sigma\left((a_k)_{k\in \{1,2\}}\right)$ denotes the vector with entries $\overline\sigma(a_1, a_2)$, applied componentwise.
The parameters consist of weight matrices and biases 
%
with appropriate dimensions to ensure compatibility. 

%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%

%
%
%
%
%
%
%
 %

Based on this construction, we have the following convexity guarantee for HyCNNs.
%

\begin{proposition}\label{prop:HyCNN_convexity}
	Let $\overline \sigma \colon \RR^2 \to \RR$ be convex and componentwise non-decreasing, and let the matrices $\{V_{\ell}^1, V_{\ell}^2\}_{\ell =0}^{L-1}$ and $V_{L}$ be componentwise non-negative. Then, $\operatorname{HyCNN} \colon \RR^d\to \RR$ in \eqref{eq:HyCNN} is convex. 
\end{proposition}

\begin{proof}
Note that $\bz_0=\mathbf{1}_d$ is a convex function of $\bx$. For the induction step, assume that each component of $\bz_\ell$ is a convex function. 
Then, since every component of $V_\ell^{k}$ is non-negative, for each $k \in \{1,2\}$
each component of $V_\ell^{k} \bz_{\ell} + W_{\ell}^{k} \bx + \bb_{\ell}^{k}$ is convex.  
Since $\overline \sigma$ is convex and componentwise non-decreasing, $\bz_{\ell+1}$ is convex as well (See Lemma~\ref{lemma_comp_convexnondecre}).
Finally, the output layer is given by a non-negative affine combination of convex functions plus an affine function, which is again a convex function. Thus, by induction, $\operatorname{HyCNN}$ is convex.
\end{proof}

The default choice for $\overline \sigma$ in analysis and experiments is the componentwise maximum,  also known as \emph{maxout unit} \citep{goodfellow2013maxout}, i.e., 
\begin{align}\label{eq:maxout}
    \overline \sigma(a_1, a_2) = \max(a_1, a_2).
\end{align}
This will result in piecewise-affine HyCNNs, which exhibit favorable approximation properties as we show in \Cref{sec:approximation}. Moreover, by choosing $\overline \sigma(a_1, a_2) = \sigma(a_1)$, where $\sigma\colon \RR \to \RR$ is a convex and non-decreasing activation function such as the ReLU, we recover the standard ICNN architecture. Hence, HyCNNs can be interpreted as a generalization of ICNNs, and enjoy similar universal approximation guarantees for convex functions as classical ICNNs derived by \citet{chen2018optimal}. 

\begin{remark}[Smooth HyCNNs]
To obtain smooth HyCNNs, we can use a smooth approximation of the max function, such as the log-sum-exp function for parameter $\tau>0$,  %
\begin{align}\label{eq:logsumexp}
    \overline \sigma_\tau(a_1, a_2) = \tau \log\left(e^{a_1/\tau} + e^{a_2/\tau}\right).
\end{align}
%
\end{remark}

\begin{remark}[Comparison with Maxout and GroupMax networks]
	HyCNNs exhibit some similarities and differences with Maxout networks \citep{goodfellow2013maxout} and GroupMax networks \citep{warin2023groupmax}. Unlike HyCNNs, in Maxout network the weights for hidden-to-hidden neuron connections are not constrained to be non-negative. Imposing this constraint results in the GroupMax network architecture. A key distinction of HyCNNs to both Maxout and GroupMax networks is the presence of (distinct) skip connections entering into both inputs of the maxout unit. This is a central technical devise in our approximation theory of the quadratic function, and seems to stabilize the gradient norm of parameters across different layers. Our empirical results in \Cref{app:regression_experiments} also suggest that this architectural change is crucial for training deeper networks.
\end{remark}

%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

\parabold{Initialization of HyCNNs}\label{sec:trainingHyCNNs} 
%
%
%
%
%
To train HyCNNs, in particular, deep architectures, the gradient norms of parameters across different layers need to be stable at initialization to mitigate the vanishing/exploding gradient problem and to ensure that all layers are effectively trained. In the following, we introduce a suitable initialization scheme, see \Cref{fig:HyCNN_profiles_init} for numerical evidence. 
%
%
%

%
%
%
%
%
%
%
%
%
%

\begin{figure}[t!]
    \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim=0 0 0 29, clip]{../figures/profile_depth_dim50_2.pdf}}
        \caption{Signal propagation and gradient profiles across relative depth in HyCNN at initialization for width $W=48$ and depths $L \in \{2,4,\ldots,16\}$ (colors) for input dimension $d = 50$.  Relative depth denotes the respective layer index normalized by network depth. 
        \textbf{(a)} Signals are computed from a single forward pass at initialization with standard Gaussian input $\bX \sim \calN(0,I_d)$. Each curve is the mean hidden-state $\ell_2$-norm of the neurons over 100 random seeds, shaded bands show the $10$th$-$$90$th percentile range. $0\%$ corresponds to the input norm $\|\bX\|_2$ (which is close to $\sqrt{d} \approx 7.07$) and $100\%$ to the final hidden layer
       \textbf{(b-d)} Gradients are computed from a single backward pass at initialization for least-squares regression on synthetic data of size $n = 1000$, with $\bX_i \sim \calN(0, I_d)$ and $Y_i = \|\bX_i\|_2^2 + \epsilon_i$, where $\epsilon_i \sim N(0,1)$. Each  curve is the mean of the gradient norm for (b) hidden-to-hidden weight, (c) skip weights, and (d) bias weights, and shaded bands show the $10$th$-$$90$th percentile range.}
         \label{fig:HyCNN_profiles_init}
         \end{center}
\end{figure}

Due to the non-negativity constraints of the hidden-to-hidden weights, standard initialization strategies based on centered weight distributions, which are commonly adopted in unconstrained neural networks \citep{lecun2002efficient, he2015delving}, are not directly applicable to HyCNNs. Inspired by the approach of \citet{hoedt2023principled} for ICNNs, we develop in the following an initialization strategy for HyCNNs. 
%
%
%
The key objective of our approach is to ensure that pre-activations exhibit comparable statistical properties across all layers at initialization.
To this end, we examine how the statistics of the pre-activations evolve from one layer to the next and derive fixed-point equations that keep their mean, variance, and covariance stable.

More specifically, for $\ell \in [L-1]$ let
\begin{align*}
    \bs_{\ell+1} = (s_{\ell+1,i})_{i \in [d_{\ell}]} := V_\ell^{1} \bz_{\ell} + W_{\ell}^{1} \bx + \bb_{\ell}^{1}, \qquad \bt_{\ell+1} = (t_{\ell+1,i})_{i \in [d_{\ell}]} := V_\ell^{2} \bz_{\ell} + W_{\ell}^{2} \bx + \bb_{\ell}^{2}.
\end{align*}
Notice that $\bz_{\ell} = \max(\bs_{\ell}, \bt_{\ell})$.
At initialization, the entries of $V_\ell^1$ and $V_\ell^2$ are drawn i.i.d.\ from a distribution supported on $\RR_+$.
The entries of $W_\ell^1$ and $W_\ell^2$ are drawn i.i.d.\ from a centered Gaussian distribution, while the entries of $\bb_\ell^1$ and $\bb_\ell^2$ are set to a fixed value.
Since the variables 
$s_{\ell,1}, t_{\ell,1}, \ldots, s_{\ell,d_\ell}, t_{\ell,d_\ell}$
are exchangeable as a collection of $2d_\ell$ variables,\footnote{A collection of random variables $x_1,\ldots,x_n$ is exchangeable if its joint distribution is invariant under permutations.} %
it is sufficient to impose the following
fixed-point equations
\begin{align*}
    \EE(s_{\ell+1,1}) = \EE(s_{\ell,1}),\qquad 
    \EE(s^2_{\ell+1,1}) = \EE(s_{\ell,1}^2),\qquad 
    \EE(s_{\ell+1,1} t_{\ell+1,1}) = \EE(s_{\ell,1} t_{\ell,1})
\end{align*}
to ensure that the mean, variance, and covariance of all neuron pre-activations are stable across layers at initialization and thus induce a well-conditioned signal propagation. 
To obtain explicit solutions to these equations, we assume that $\|\bx\|^2_2 \approx d$ and use a Gaussian approximation of the joint distribution of $s_{\ell,1},\ldots,s_{\ell,d_{\ell}},t_{\ell,1},\ldots,t_{\ell,d_{\ell}}.$ 

\textit{Initialization scheme for HyCNNs:}
%
\begin{itemize}[leftmargin=1.5em, labelsep=0.5em]
    \item The entries of $V_\ell^1$ and $V_\ell^2$ for $\ell \in [L-1]$ are drawn i.i.d. from a distribution supported on $\RR_+$ with mean and variance, respectively, given by
    $$\mu := \sqrt{\frac{1}{d_{\ell}^2 + (1-\tfrac{1}{\pi})d_{\ell}}}, \quad \sigma^2 := \frac{1}{4d_{\ell}}.$$ 
    We take the log-normal distribution as it is easy to sample from. %
    The above constraints are then realized by drawing
    $$X\coloneqq \exp(\tilde X), \quad  \tilde{X} \sim \mathcal{N}\left( \ln\Big(\frac{\mu^2}{\sqrt{\tau}}\Big), \ln\Big(\frac{\tau}{\mu^2}\Big)\right) \quad \text{ with }\, \tau\coloneqq \mu^2 + \sigma^2,$$
    where $\calN(\mu, \sigma^2)$ denotes the normal distribution with mean $\mu$ and variance $\sigma^2.$
    \item The entries of $W_\ell^1$ and $W_\ell^2$  for $\ell \in [L-1]$ are drawn i.i.d. from $\calN(0, 1/(4d))$.
    \item The entries of $\bb_\ell^1$ and $\bb_\ell^2$  for $\ell \in [L-1]$ are set to $-\sqrt{\frac{d_{\ell}}{2 \pi d_{\ell} + 2 \pi -2}}$. 
    \item The parameters $V_L^0, W_L^0, \bb_L^0$ in the last layer use the same initialization scheme.
    \item The parameters $W_0^{1},W_0^{2}$ and $\bb_0^{1}, \bb_0^{2}$ in the first layer adopt the initialization of \citet{lecun2002efficient}  (i.e., entries are i.i.d.\ samples from $N(0,1/d)$).
\end{itemize}
%
%
%
%
%

%
%
%
%
%
%
%

Derivations are provided in Appendix~\ref{appendix_init}. We note that the initialization scheme for HyCNNs is motivated by that of ICNNs proposed by \citet{hoedt2023principled}, but tailored to the architectural differences of HyCNNs. 
%
Based on this initialization scheme, we empirically verify that the signals across different layers are stable at initialization (see Figure \ref{fig:HyCNN_profiles_init}(a)), which is crucial for training deep networks. For a visualization of HyCNN at initialization across different depths see \Cref{fig:HyCNN_init_vis}. 
%
%

%

%
%

\section{Approximation of Quadratic Functions}\label{sec:approximation}

The quadratic function $x\mapsto x^2$ is fundamental for approximating more complex convex functions, and thus serves as a natural testbed for understanding the approximation capabilities of convex neural architectures. 
In the following we analyze the capabilities of ICNNs and HyCNNs in approximating the quadratic function on the unit interval $[0,1]$.  While the focus of this section is on the univariate setting for simplicity, the results can be easily extended to the multivariate setting, and we discuss this in \Cref{app:QuantitativeApprox}. All proofs of this section are deferred to Appendix~\ref{app:proofs}.

%

\parabold{Limited Expressivity of ICNNs} 
A preliminary observation is that (standard or leaky) ReLU ICNNs are piecewise-affine, and the number of linear pieces grows only linearly with the number of layers. Recall that a leaky ReLU is defined as $\sigma(x) = \max(\alpha x, x)$ for some $\alpha \in (0,1)$.

\begin{proposition} \label{prop:piecewise_linear_icnn}
Consider an  ICNN $f \colon \RR\to \RR$ with $L$ hidden layers and $d_\ell$ neurons on layer $\ell$, whose activation function is given by a (standard or leaky) ReLU. Then, $f$ is piecewise-affine with at most $d_1 + 2d_2 + \dots + 2d_L$ pieces.
\end{proposition}

\begin{theorem}\label{thm:lowerBoundPiecewiseLinear}
    Let $\calG_k$ be the set of real-valued, piecewise-affine, convex functions on $[0,1]$ with at most $k$ pieces.
    Then,     \begin{align}\label{eq:lowerBoundApproxPiecewiseLinear}
       \inf_{g\in \calG_k} \, \int_{0}^1 \big|g(x)-x^2 \big| \, dx \geq \frac{1}{16 k^2}, \quad \text{ and } \quad
       \inf_{g\in \calG_k} \, \sup_{x\in [0,1]} \, |g(x)-x^2| \geq \frac{1}{8 k^2}.
    \end{align}
    In particular, any (standard or leaky) ReLU ICNN $f\colon \RR\to \RR$ with $L$ hidden layers and $d_\ell$ neurons in layer $\ell$ satisfies
    \begin{align*}
    \int_{0}^1 \big|f(x)-x^2 \big| \, dx \geq \frac{1}{16(d_1 + 2 \sum_{\ell = 2}^L d_\ell)^2} \quad \text{and} \quad 
    \sup_{x\in [0,1]}|f(x)-x^2| \geq \frac{1}{8 (d_1 + 2 \sum_{i = 2}^L d_\ell)^2}.
    \end{align*}
\end{theorem}

%

%
%
%
%
    

\parabold{Expressivity of HyCNNs} 
Next, we focus on the approximation capabilities of HyCNNs.

\begin{theorem}[Quadratic Function Approximation]\label{thm:quadratic_approximation}
	For any $L\in \NN$ and even numbers $d_1, \ldots, d_L$, there exists a HyCNN $h \colon \RR\to \RR$ with $\overline \sigma(a,b) = \max(a,b)$,  $L$ hidden layers, and $(d_1, \dots, d_L)$ neurons per layer %
    such that 
     \begin{align*} 
        \sup_{x\in [0,1]}|h(x) - x^2| \leq \frac{1}{8\prod_{\ell=1}^L d_{\ell}^2}.
     \end{align*}
\end{theorem}

%
    %
    %
    A first key takeaway from \Cref{thm:quadratic_approximation} is that wider HyCNNs lead to a \emph{polynomial} increase of the approximation accuracy, while deeper networks lead to an \emph{exponential} increase of the approximation accuracy. In particular, HyCNNs are able to \emph{leverage depth} for approximation, which is in stark contrast to ICNNs. Our empirical findings show that deeper HyCNNs can also be effectively trained. %

\begin{remark}[Interpretation of Theorem \ref{thm:quadratic_approximation}]
    The proof is detailed in Supplement \ref{app:proofs}. A similar result is well-known for feedforward ReLU networks. However, the known construction crucially relies on highly oscillating sawtooth functions, which are not input convex \citep{telgarsky2016, yarotski2017, schmidthieber2017}. It is therefore surprising that each HyCNN with at least two neurons per layer can at least \emph{double} the number of linear pieces in the piecewise-affine approximation of $x^2$, leading to an exponential decay of the approximation error with respect to the number of layers. To explain why it works, we derive a second proof for the case $d_1=\ldots=d_L=2$ that reveals how the oscillatory functions can be cached in input convex functions. %
    %
\end{remark}

Based on our construction for the quadratic function, we also obtain an efficient approximation of higher order monomials $x\mapsto x^n$ on $[0,1]$ for $n=2,3,\ldots$ by suitably concatenating HyCNN blocks. %

\begin{theorem}[Monomial Function Approximation]\label{thm_monomial}
    For any integer $n \geq 2$, $L\in \NN$ and odd number $m \geq 3$, there exists a HyCNN $h \colon \RR\to \RR$ with $\overline \sigma(a,b) = \max(a,b)$, $ \lceil \log_2(n)\rceil L$ layers and $m$ neurons per layer such that 
    \begin{align*}
        \sup_{x\in [0,1]} \big|h(x) - x^n\big| \leq \frac{n}{2} (m-1)^{-2L}.
    \end{align*}
\end{theorem}
%

The underlying HyCNN construction is not a straightforward extension of the network construction for the quadratic function (\Cref{thm:quadratic_approximation}), and requires a more involved proof strategy. This is in contrast to feedforward ReLU networks where the approximation of, say, $x\mapsto x^3$ first constructs a network approximately computing $x\mapsto (x,x^2)$ and then concatenates the outcome with a multiplication network that approximates the map $(u,v)\mapsto uv,$ therefore computing approximately $x\mapsto x x^2 =x^3.$ However,  $(u,v)\mapsto uv$ is not a convex function and therefore not representable by a HyCNN. 

%

%

%

%
%

We close this section with further implications of the above results. 
Denote by $\ICNN_d(L,m)$, $\HyCNN_d(L,m)$ and $\ReLU_d(L,m)$ the respective classes of all (ReLU) ICNNs, (maxout) HyCNNs and ReLU networks with $d$ input neurons, $L$ hidden layers and $m$ neurons per layer, respectively. As a direct consequence of Theorems \ref{thm:lowerBoundPiecewiseLinear} and \ref{thm:quadratic_approximation} we have that whenever $m'$ is even and $(m')^{L'} \geq 2mL,$
    \begin{align}
        \HyCNN_d(L',m') \subsetneq \ICNN_d(L,m) \subseteq \HyCNN_d(L,m)
        \subseteq \ReLU_d(L,3m+2d).
        \label{eq.84gr}
    \end{align}
    This shows that a much larger number of ICNN parameters is needed to represent all HyCNN functions. The $\subsetneq$ part also reveals that ICNNs are limited in their ability to represent the maximum of two functions as otherwise they could emulate HyCNNs contradicting \eqref{eq.84gr}.   
    The last inclusion implies that any lower bound on the approximation error of ReLU networks directly translate to those of HyCNNs. Moreover, known bounds on the VC dimension and covering number of ReLU networks can be used to derive corresponding bounds for HyCNNs.
    A formal proof of \eqref{eq.84gr} can be found in Appendix~\ref{appendix_proof_equation_inclusion}. 

  %

%
%
%
%
%
%
%
%
%
%
%
%
%
    
%

%

%
%
%
%
%

%

%

\section{Application: Neural Optimal Transport Map Learning}\label{sec:applications}

%

%
%
%
%
%

%
%

%
%
%
%
%
%
%
%

%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
\label{sec:neural_ot}

Learning an optimal transport (OT) map between probability measures is a central problem with broad impact in machine learning \citep{courty2016optimal,gordaliza2019obtaining}, statistics \citep{hallin2021distribution,de2024transport}, and natural sciences \citep{wang2010optimal,schiebinger2019optimal,tameling2021colocalization,bunne2023learning}.  
To formalize the problem, take probability measures $P$ and $Q$ be on $\RR^d$ with finite second moments. For squared Euclidean costs, the \emph{OT map} is defined as%
\begin{equation*}
  \overline T \in \argmin_{T:\,T_\# P = Q}\; \int_{\RR^d}\|\bx-T(\bx)\|^2\,dP(\bx), \quad \text{ where } T_\# P \coloneqq P\circ T^{-1}, 
\end{equation*} assuming it exists. If $P$ and $Q$ are absolutely continuous, Brenier's theorem \citep[Theorem 1.22]{santambrogio2015optimal} guarantees the existence of a $P$-a.s.\ unique convex potential $\phi:\RR^d\to\RR$, the \emph{OT potential}, such that $\overline T = \nabla \phi$. This links OT map estimation with learning the OT potential.

Recent work has produced a variety of estimators for $\overline T$, including plug-in methods \citep{manole2024plugin}, entropic approaches \citep{seguy2017large,pooladian2021entropic}, semi-dual formulations \citep{hutter2021minimax,divol2025optimal}, and neural estimators \citep{taghvaei20192,makkuva2020optimal,bunne2023learning,uscidda2023monge}. It is worth noting that empirical plug-in and entropic estimators, though adaptive to low-dimensional structures \citep{weed2019sharp,hundrieser2024empirical,groppe2024lower,stromme2024minimum,divol2025optimal} are oftentimes outperformed by neural estimators in genuinely high-dimensional settings \citep{makkuva2020optimal,uscidda2023monge}, which motivates the use of neural OT in this regime.

%
We use the variational formulation of \citet{makkuva2020optimal}, based on the semidual framework by \cite{hutter2021minimax}, which characterizes the OT potential $\phi$ via a saddle-point problem, 
\begin{align*}
  \phi \in \underset{\text{convex } f\in L^1(P),f^*\in L^1(Q)}{\argmax}
  \;\; \underset{\vphantom{f^*}g\in L^1(Q)\vphantom{f^*}}{\vphantom{g}\inf\vphantom{g}}\; -\EE_{\bX\sim P}[f(\bX)]
  -\EE_{\bY\sim Q}\!\big[\langle \bY,\nabla g(\bY)\rangle - f(\nabla g(\bY))\big]. 
\end{align*}
Given $f$, the optimal $g$ corresponds to the convex conjugate of $f$, i.e., $g = f^*$. In practice, we replace the expectations by empirical averages (using mini-batches), and the function classes are restricted to neural network families. %
Denoting the training data $(\bx_i)_{i=1}^n\sim P$ and $(\by_j)_{j=1}^m\sim Q$, we follow the mini-batch training protocol of \citet{makkuva2020optimal} but replace the ICNNs by  HyCNNs with smooth gated activation function $\overline\sigma_\tau(a_1,a_2) = \tau \log(e^{a_1/\tau} + e^{a_2/\tau})$. This leads to a saddle-point problem for  mini-batches $(\bX_i)_{i=1}^M$ and $(\bY_j)_{j=1}^M$ from $(\bx_i)_{i=1}^n$ and $(\by_j)_{j=1}^m$, respectively, of size $M\in \NN$, 
%
%
\begin{align}\label{eq:HyCNN_OT_potential_estimation}
  \hat\phi \in &
  \argmax_{f\in \texttt{HyCNN}_\tau(\RR^d)}
  \;\underset{{g\in \texttt{HyCNN}_\tau(\RR^d)}}{\vphantom{g}\min\vphantom{g}}\;
  \textstyle -\frac{1}{M}\left(\sum_{i = 1}^{M} f(\bX_i)+\langle \bY_i, \nabla g(\bY_i)\rangle - f(\nabla g(\bY_i)) \right).
\end{align}
The \textit{HyCNN based OT map estimator} is then defined by $\hat T \coloneqq \nabla \hat \phi$, see \Cref{fig:HyCNN_OT_shapes_2d} for an illustration. The training method is detailed in \Cref{alg:HyCNN_ot} in \Cref{app:OT_implementation}, it uses Adam \citep{kingma2014adam} and involves an outer loop (with $T$ iterations) and an inner loop (with $S$ iterations per outer iteration). During training we parametrize hidden-to-hidden weights via a softplus function to ensure non-negativity, deviating from the approach by \citet{makkuva2020optimal} who use a regularization term for a soft-enforcement of non-negativity. 
%
%

%

\begin{figure}[t!]
    \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim=0 16 0 5, clip]{../figures/combined_sweep.pdf}}
        \caption{Pushforwards under learned HyCNN OT map (width $48$, depth $4$). The HyCNN is trained for $n = m = M = 2000$ data points for $2500$ outer iterations for learning $f$, with $S = 10$ steps per iterations for learning $g$, via Adam and decaying learning rates and smoothness parameter $\tau$. 
        }
         \label{fig:HyCNN_OT_shapes_2d}
         \end{center}
\end{figure}

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%

%

%

%

%
%
%
%
%
%
%
%
%

%
%
%
%
%

%

\begin{figure}[b!]
%
  \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim = 0 0 0 0, clip]{../figures/FIG_4_MSE_vs_NTrain_multitask_best_at_n10000.pdf}}
    %
    \caption{Prediction MSE for different training sample sizes $n$ for the $50$-dimensional regression tasks with 10th-90th percentile bands across $10$ runs. Each panel shows HyCNNs with depths $2,4,8,16$ and the best MLP, ICNN, GMN at $n = 10^4$ among depths $\in \{2,4,8,16\}$. %
    }
    \label{fig:HyCNN_training_dim50}
  \end{center}
  \vspace{-5mm}
\end{figure}

\section{Experiments}\label{sec:experiments}

%

%

%

\parabold{Convex regression} 
We draw covariates $(\bX_i)_{i=1}^n$ from $\textup{Unif}[-1,1]^d$ with responses according to the model $Y_i = f(\bX_i) + \epsilon_i$, where $\epsilon_i\in N(0,\sigma^2)$ are independent Gaussian errors with standard deviation $\sigma\geq 0$, and $f\colon \RR^d \to \RR$ is one of the following functions, 
\begin{align*}
   &\textstyle \text{(a) } f_1(\bx) = \|\bx\|^2_2, &&\text{(b) } f_2(\bx) = \|\bx\|_4^4, \;&&\text{(c) } f_3(\bx) = \|\bx\|^2_2 + 0.25\sin\left(20\|\bx\|_2\right)%
%
\end{align*}
%
Note that $f_3$ is not convex, but it can be nonetheless approximated by a convex function. In \Cref{fig:HyCNN_training_dim50} we display the prediction MSE for an independent testing set for $f_1, f_2, f_3$ for $d = 50$ and with $\sigma = 1$ for $f_1, f_2$ and $\sigma = 0$ for $f_3$ and training sample size $n \in \{100, 200, 500, 1000, 2000, 5000, 10000\}$. For each regression setting, we train feedforward ReLU networks (multilayer perceptrons, MLPs), ICNNs \citep{amos2017input}, GroupMaxNets (GMNs, \citealt{warin2023groupmax}, i.e., HyCNNs without skip connections from the input), and HyCNNs. For the MLPs and ICNNs we consider width $m = 64$ whereas for GroupMaxNets and HyCNNs we consider width $m = 48$, as GroupMaxNets and HyCNNs require approximately twice as many parameters as other models with the same width. Further we consider depth $L \in \{2, 4, 8, 16,32\}$ for all architectures. %
HyCNNs with depth at least four consistently outperform all other methods across all regression settings, with deeper HyCNNs performing better than shallower ones. The same findings are observed in an extensive simulation study in \Cref{app:additional_experiments}.

%
%
%
%
%
%
%

%

%

%
%

%

%



\parabold{Neural OT map estimation}
To assess the performance of the HyCNN-based OT map estimator, we consider the following OT potentials with corresponding OT maps given by their gradients,
\begin{align*}
    &\textstyle \text{(a) } \textstyle\phi_1(\bx) = \frac{\|\bx\|^2_2}{2}, \quad T_1(\bx) =  \bx, &&\text{(b) } \textstyle\phi_2(\bx) = \frac{1}{2}\sum_{i = 1}^{d} \big(1+ \frac{\sin(i)}{2}\big)x_i^2, \quad T_2(\bx) = \big((1+\frac{\sin(i)}{2})x_i\big)_{i=1}^d, %
\end{align*}
and draw $n=m = 5000$ independent samples from $P = N(0, I_d)$ and $Q = (\nabla \phi_\ell)_\# P$ for $\ell \in \{1,2\}$ for $d = 50$. In \Cref{fig:HyCNN_training_OT}\textbf{(a)} we display the (dimension-normalized) prediction MSE for an independent testing set for the four OT map estimation tasks for $d = 50$ across training iterations. We compare the performance of HyCNNs with widths $48$ and depths $4$ and smoothness parameter $\tau = 10$ with multiple variants of ICNNs \citep{makkuva2020optimal}, and the Monge Gap MLP estimator \citep{uscidda2023monge}, all with widths $64$ and depths $L \in \{2, 4,6\}$. HyCNNs outperform all other methods across all tasks, with ICNNs performing better than the Monge Gap MLP estimator. Moreover, for the 4i single-cell imaging dataset, preprocessed by \cite{bunne2023learning}, we train HyCNNs and ICNNs to map the unperturbed control distribution onto each drug-perturbed distribution and find that HyCNNs attains a lower Sinkhorn divergence  on a $20\%$ held-out test partition than the best ICNN baseline across nearly all considered perturbations, see \Cref{fig:HyCNN_training_OT}\textbf{(b)} or \Cref{fig:HyCNN_training_OT_large} for an enlarged view. Details on training rules and further aspects on the data analysis are given in  Appendices \ref{app:additional_experiments} and \ref{app:single_cell}. To make the comparison robust to variability across checkpoints, each reported value averages the test-set Sinkhorn divergence over the $K = 10$ checkpoints with smallest validation loss; see Appendix \ref{app:single_cell} for details.
\Cref{fig:HyCNN_training_OT}\textbf{(b)} contrasts a short and a long training schedule per architecture. Longer training improves performance, but architecture outweighs training budget: with $100$ times less compute, the short HyCNN competes with the long ICNN, and is outperformed by the long HyCNN.

\begin{figure}[h!]
%
  \begin{center}
    \centerline{%
    %
    \includegraphics[width=\textwidth, trim = 0 0 0 0, clip]{../figures/OT_Sims_4i_5.pdf}}
    %
    \caption{Performance of OT map estimation for synthetic and 4i single cell RNA-seq data. \textbf{(a)}. Prediction MSE (normalized by dimension $d=50$) for $n = 5000$ training samples for OT map estimation  tasks with 10th-90th percentile bands across $10$ runs. 
    Both panels show the same HyCNN and the best ICNN with ReLU or leaky ReLU, or with a quadratic term in the first layer with ReLU or Softplus, and the Monge Gap MLP estimator, each within a class of width $64$, depths $L \in \{2, 4,6\}$ and $\tau \in \{0.1, 1, 10\}$. \textbf{(b)} Sinkhorn divergence between predicted and ground-truth drug-perturbed distributions on a $20\%$ held-out test partition of the 4i dataset for each drug based on ICNN ($64\times4$, Softplus, $\tau = 1$, Quad) and HyCNN ($48\times 4$, logsumexp, $\tau = 1$) trained for $T = 1,000$ outer iterations and $S = 5$ inner iterations (short) as well as $T = 50,000$ iterations and $S = 10$ inner iterations (long). %
    }
    \label{fig:HyCNN_training_OT}
  \end{center}
  \vspace{-5mm}
\end{figure}

%
%
%
%
%
%
%
%
%
%

%

%

%

%

%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%

%

%

%

%
%
%

%
%

%

%

%

%

%
%
%
%
%
%
%

%
%
%

%

%

\section{Discussion and Limitations}\label{sec:limitations}
HyCNNs appear as a promising architecture for learning convex functions in high dimensions: for regression, deeper models perform better than shallower ones, and for OT map estimation, HyCNNs with large $\tau$ perform better than those with small $\tau$. 
%
We note two limitations of our work. By construction, HyCNNs exhibit an inductive bias toward smooth, coercive convex functions, which benefits many applications but may constrain training in settings that deviate from these assumptions. Further, we note that our empirical study is bounded by computational constraints: though we conducted extensive simulations, our training were still limited, and a more large-scale study remains an future step.
%
%

%

%

\section*{Acknowledgements}
\addcontentsline{toc}{section}{Acknowledgements}
S.\ Hundrieser is funded from the German National Academy of Sciences Leopoldina under grant number LPDS 2024-11. I.\ Kong and J.\ Schmidt-Hieber are supported
by ERC grant A2B (grant agreement number 101124751). S.\ Hundrieser further acknowledges helpful discussions with Paul Hagemann in an early phase of this project. 
%
%\bibliography{biblio}
%\bibliographystyle{settings/apalike2}


\addcontentsline{toc}{section}{References}

\begin{thebibliography}{}

\bibitem[Amos et~al., 2017]{amos2017input}
Amos, B., Xu, L., \& Kolter, J.~Z. (2017).
\newblock Input convex neural networks.
\newblock In {\em International conference on machine learning}  \!\!, pages 146--155.: PMLR.

\bibitem[Bal{\'a}zs et~al., 2015]{balazs2015near}
Bal{\'a}zs, G., Gy{\"o}rgy, A., \& Szepesv{\'a}ri, C. (2015).
\newblock Near-optimal max-affine estimators for convex regression.
\newblock In {\em Artificial Intelligence and Statistics}  \!\!, pages 56--64.: PMLR.

\bibitem[Brenier, 1991]{brenier1991polar}
Brenier, Y. (1991).
\newblock Polar factorization and monotone rearrangement of vector-valued functions.
\newblock {\em Communications on pure and applied mathematics}, 44(4), 375--417.

\bibitem[Bunne et~al., 2023]{bunne2023learning}
Bunne, C., Stark, S.~G., Gut, G., Del~Castillo, J.~S., Levesque, M., Lehmann, K.-V., Pelkmans, L., Krause, A., \& R{\"a}tsch, G. (2023).
\newblock Learning single-cell perturbation responses using neural optimal transport.
\newblock {\em Nature methods}, 20(11), 1759--1768.

\bibitem[Chen et~al., 2018]{chen2018optimal}
Chen, Y., Shi, Y., \& Zhang, B. (2018).
\newblock Optimal control via neural networks: A convex approach.
\newblock {\em Preprint arXiv:1805.11835}.

\bibitem[Courty et~al., 2016]{courty2016optimal}
Courty, N., Flamary, R., Tuia, D., \& Rakotomamonjy, A. (2016).
\newblock Optimal transport for domain adaptation.
\newblock {\em IEEE transactions on pattern analysis and machine intelligence}, 39(9), 1853--1865.

\bibitem[Cuturi et~al., 2022]{cuturi2022optimal}
Cuturi, M., Meng-Papaxanthos, L., Tian, Y., Bunne, C., Davis, G., \& Teboul, O. (2022).
\newblock Optimal transport tools ({OTT}): A {JAX} toolbox for all things {W}asserstein.
\newblock {\em Preprint arXiv:2201.12324}.

\bibitem[De~Lara et~al., 2024]{de2024transport}
De~Lara, L., Gonz{\'a}lez-Sanz, A., Asher, N., Risser, L., \& Loubes, J.-M. (2024).
\newblock Transport-based counterfactual models.
\newblock {\em Journal of Machine Learning Research}, 25(136), 1--59.

\bibitem[Deschatre \& Warin, 2025]{deschatre2025input}
Deschatre, T. \& Warin, X. (2025).
\newblock Input convex {Kolmogorov Arnold Networks}.
\newblock {\em Preprint arXiv:2505.21208}.

\bibitem[Divol et~al., 2025]{divol2025optimal}
Divol, V., Niles-Weed, J., \& Pooladian, A.-A. (2025).
\newblock Optimal transport map estimation in general function spaces.
\newblock {\em The Annals of Statistics}, 53(3), 963--988.

\bibitem[Eckle \& Schmidt-Hieber, 2019]{eckle2019comparison}
Eckle, K. \& Schmidt-Hieber, J. (2019).
\newblock A comparison of deep networks with {ReLU} activation function and linear spline-type methods.
\newblock {\em Neural Networks}, 110, 232--242.

\bibitem[Feng et~al., 2026]{feng2024optimal}
Feng, O.~Y., Kao, Y.-C., Xu, M., \& Samworth, R.~J. (2026).
\newblock Optimal convex m-estimation via score matching.
\newblock {\em The Annals of Statistics}, 54(1), 408--441.

\bibitem[Feydy et~al., 2019]{feydy2019interpolating}
Feydy, J., S{\'e}journ{\'e}, T., Vialard, F.-X., Amari, S.-i., Trouv{\'e}, A., \& Peyr{\'e}, G. (2019).
\newblock Interpolating between optimal transport and {MMD} using {Sinkhorn} divergences.
\newblock In {\em The 22nd international conference on artificial intelligence and statistics}  \!\!, pages 2681--2690.: PMLR.

\bibitem[Goodfellow et~al., 2013]{goodfellow2013maxout}
Goodfellow, I., Warde-Farley, D., Mirza, M., Courville, A., \& Bengio, Y. (2013).
\newblock Maxout networks.
\newblock In S. Dasgupta \& D. McAllester (Eds.), {\em Proceedings of the 30th International Conference on Machine Learning}, number 28(3) in Proceedings of Machine Learning Research  \!\!, pages 1319--1327.

\bibitem[Gordaliza et~al., 2019]{gordaliza2019obtaining}
Gordaliza, P., Del~Barrio, E., Fabrice, G., \& Loubes, J.-M. (2019).
\newblock Obtaining fairness using optimal transport theory.
\newblock In {\em International conference on machine learning}  \!\!, pages 2357--2365.: PMLR.

\bibitem[Groppe \& Hundrieser, 2024]{groppe2024lower}
Groppe, M. \& Hundrieser, S. (2024).
\newblock Lower complexity adaptation for empirical entropic optimal transport.
\newblock {\em Journal of Machine Learning Research}, 25(344), 1--55.

\bibitem[Guntuboyina \& Sen, 2015]{guntuboyina2015global}
Guntuboyina, A. \& Sen, B. (2015).
\newblock Global risk bounds and adaptation in univariate convex regression.
\newblock {\em Probability Theory and Related Fields}, 163(1), 379--411.

\bibitem[Hallin et~al., 2021]{hallin2021distribution}
Hallin, M., del Barrio, E., Cuesta-Albertos, J., \& Matr{\'a}n, C. (2021).
\newblock Distribution and quantile functions, ranks and signs in dimension $d$.
\newblock {\em The Annals of Statistics}, 49(2), 1139--1165.

\bibitem[Hannah \& Dunson, 2013]{hannah2013multivariate}
Hannah, L.~A. \& Dunson, D.~B. (2013).
\newblock Multivariate convex regression with adaptive partitioning.
\newblock {\em Journal of Machine Learning Research}, 14(1), 3261--3294.

\bibitem[He et~al., 2015]{he2015delving}
He, K., Zhang, X., Ren, S., \& Sun, J. (2015).
\newblock Delving deep into rectifiers: Surpassing human-level performance on imagenet classification.
\newblock In {\em Proceedings of the IEEE international conference on computer vision}  \!\!, pages 1026--1034.

\bibitem[Hoedt \& Klambauer, 2023]{hoedt2023principled}
Hoedt, P.-J. \& Klambauer, G. (2023).
\newblock Principled weight initialisation for input-convex neural networks.
\newblock {\em Advances in Neural Information Processing Systems}, 36, 46093--46104.

\bibitem[Huang et~al., 2020]{huang2020convex}
Huang, C.-W., Chen, R.~T., Tsirigotis, C., \& Courville, A. (2020).
\newblock Convex potential flows: {Universal} probability distributions with optimal transport and convex optimization.
\newblock {\em Preprint arXiv:2012.05942}.

\bibitem[Hundrieser et~al., 2024]{hundrieser2024empirical}
Hundrieser, S., Staudt, T., \& Munk, A. (2024).
\newblock Empirical optimal transport between different measures adapts to lower complexity.
\newblock {\em Annales de l'Institut Henri Poincare (B) Probabilites et statistiques}, 60(2), 824--846.

\bibitem[H{\"u}tter \& Rigollet, 2021]{hutter2021minimax}
H{\"u}tter, J.-C. \& Rigollet, P. (2021).
\newblock Minimax estimation of smooth optimal transport maps.
\newblock {\em The Annals of Statistics}, 49(2), 1166--1194.

\bibitem[Hyv{\"a}rinen, 2005]{hyvarinen2005estimation}
Hyv{\"a}rinen, A. (2005).
\newblock Estimation of non-normalized statistical models by score matching.
\newblock {\em Journal of Machine Learning Research}, 6(4).

\bibitem[Kingma \& Ba, 2014]{kingma2014adam}
Kingma, D.~P. \& Ba, J. (2014).
\newblock Adam: A method for stochastic optimization.
\newblock {\em Preprint arXiv:1412.6980}.

\bibitem[LeCun et~al., 2002]{lecun2002efficient}
LeCun, Y., Bottou, L., Orr, G.~B., \& M{\"u}ller, K.-R. (2002).
\newblock Efficient backprop.
\newblock In {\em Neural networks: Tricks of the trade}  \!\!, pages 9--50. Springer.

\bibitem[Liang \& Srikant, 2017]{liang2017why}
Liang, S. \& Srikant, R. (2017).
\newblock Why deep neural networks for function approximation?
\newblock In {\em International Conference on Learning Representations}.
\newblock https://openreview.net/forum?id=SkpSlKIel.

\bibitem[Lin \& Ba, 2023]{lin2023falcon}
Lin, A. \& Ba, D.~E. (2023).
\newblock How to train your {FALCON}: Learning log-concave densities with energy-based neural networks.
\newblock In {\em Fifth Symposium on Advances in Approximate Bayesian Inference}.

\bibitem[Makkuva et~al., 2020]{makkuva2020optimal}
Makkuva, A., Taghvaei, A., Oh, S., \& Lee, J. (2020).
\newblock Optimal transport mapping via input convex neural networks.
\newblock In {\em International Conference on Machine Learning}  \!\!, pages 6672--6681.: PMLR.

\bibitem[Manole et~al., 2024]{manole2024plugin}
Manole, T., Balakrishnan, S., Niles-Weed, J., \& Wasserman, L. (2024).
\newblock Plugin estimation of smooth optimal transport maps.
\newblock {\em The Annals of Statistics}, 52(3), 966--998.

\bibitem[McClure, 1975]{mcclure1975nonlinear}
McClure, D.~E. (1975).
\newblock Nonlinear segmented function approximation and analysis of line patterns.
\newblock {\em Quarterly of Applied Mathematics}, 33(1), 1--37.

\bibitem[{Nesterov} et~al., 2022]{nesterov2022learning}
{Nesterov}, V., {Arend Torres}, F., {Nagy-Huber}, M., {Samarin}, M., \& {Roth}, V. (2022).
\newblock {Learning invariances with generalised input-convex neural networks}.
\newblock {\em Preprint arXiv:2204.07009}.

\bibitem[Peyr{\'e} \& Cuturi, 2019]{peyre2019computational}
Peyr{\'e}, G. \& Cuturi, M. (2019).
\newblock Computational optimal transport: With applications to data science.
\newblock {\em Foundations and Trends{\textregistered} in Machine Learning}, 11(5-6), 355--607.

\bibitem[Pooladian \& Niles-Weed, 2021]{pooladian2021entropic}
Pooladian, A.-A. \& Niles-Weed, J. (2021).
\newblock Entropic estimation of optimal transport maps.
\newblock {\em Preprint arXiv:2109.12004}.

\bibitem[Rezende \& Mohamed, 2015]{rezende2015variational}
Rezende, D. \& Mohamed, S. (2015).
\newblock Variational inference with normalizing flows.
\newblock In {\em International conference on machine learning}  \!\!, pages 1530--1538.: PMLR.

\bibitem[Samworth, 2018]{samworth2018recent}
Samworth, R.~J. (2018).
\newblock Recent progress in log-concave density estimation.
\newblock {\em Statistical Science}, 33(4), 493.

\bibitem[Santambrogio, 2015]{santambrogio2015optimal}
Santambrogio, F. (2015).
\newblock {\em Optimal transport for applied mathematicians. {Calculus of variations, PDEs, and modeling}}.
\newblock Birkh{\"a}user Basel.

\bibitem[Schiebinger et~al., 2019]{schiebinger2019optimal}
Schiebinger, G., Shu, J., Tabaka, M., Cleary, B., Subramanian, V., Solomon, A., Gould, J., Liu, S., Lin, S., Berube, P., Lee, L., Chen, J., Brumbaugh, J., Rigollet, P., Hochedlinger, K., Jaenisch, R., Regev, A., \& Lander, E.~S. (2019).
\newblock Optimal-transport analysis of single-cell gene expression identifies developmental trajectories in reprogramming.
\newblock {\em Cell}, 176(4), 928--943.

\bibitem[Schmidt-Hieber, 2020]{schmidthieber2017}
Schmidt-Hieber, J. (2020).
\newblock Nonparametric regression using deep neural networks with {ReLU} activation function.
\newblock {\em The Annals of Statistics}, 48(4), 1875--1897.

\bibitem[Seguy et~al., 2017]{seguy2017large}
Seguy, V., Damodaran, B.~B., Flamary, R., Courty, N., Rolet, A., \& Blondel, M. (2017).
\newblock Large-scale optimal transport and mapping estimation.
\newblock {\em Preprint arXiv:1711.02283}.

\bibitem[Seijo \& Sen, 2011]{seijo2011convex}
Seijo, E. \& Sen, B. (2011).
\newblock Nonparametric least squares estimation of a multivariate convex regression function.
\newblock {\em The Annals of Statistics}, 39(3), 1633--1657.

\bibitem[Sivaprasad et~al., 2021]{sivaprasad2021curious}
Sivaprasad, S., Singh, A., Manwani, N., \& Gandhi, V. (2021).
\newblock The curious case of convex neural networks.
\newblock In {\em Joint European Conference on Machine Learning and Knowledge Discovery in Databases}  \!\!, pages 738--754.: Springer.

\bibitem[Song et~al., 2021]{song2021score}
Song, Y., Durkan, C., Murray, I., \& Ermon, S. (2021).
\newblock Maximum likelihood training of score-based diffusion models.
\newblock In M. Ranzato, A. Beygelzimer, Y. Dauphin, P. Liang, \& J.~W. Vaughan (Eds.), {\em Advances in Neural Information Processing Systems}, volume~34  \!\!, pages 1415--1428.

\bibitem[Stromme, 2024]{stromme2024minimum}
Stromme, A.~J. (2024).
\newblock Minimum intrinsic dimension scaling for entropic optimal transport.
\newblock In {\em International Conference on Soft Methods in Probability and Statistics}  \!\!, pages 491--499.: Springer.

\bibitem[Taghvaei \& Jalali, 2019]{taghvaei20192}
Taghvaei, A. \& Jalali, A. (2019).
\newblock 2-{Wasserstein} approximation via restricted convex potentials with application to improved training for {GANs}.
\newblock {\em Preprint arXiv:1902.07197}.

\bibitem[Tameling et~al., 2021]{tameling2021colocalization}
Tameling, C., Stoldt, S., Stephan, T., Naas, J., Jakobs, S., \& Munk, A. (2021).
\newblock Colocalization for super-resolution microscopy via optimal transport.
\newblock {\em Nature computational science}, 1(3), 199--211.

\bibitem[Tan et~al., 2023]{tan2023data}
Tan, H.~Y., Mukherjee, S., Tang, J., \& Sch{\"o}nlieb, C.-B. (2023).
\newblock Data-driven mirror descent with input-convex neural networks.
\newblock {\em SIAM Journal on Mathematics of Data Science}, 5(2), 558--587.

\bibitem[Telgarsky, 2016]{telgarsky2016}
Telgarsky, M. (2016).
\newblock Benefits of depth in neural networks.
\newblock In V. Feldman, A. Rakhlin, \& O. Shamir (Eds.), {\em 29th Annual Conference on Learning Theory}, volume~49 of {\em Proceedings of Machine Learning Research}  \!\!, pages 1517--1539.  Columbia University, New York, New York, USA: PMLR.

\bibitem[Thakolkaran et~al., 2025]{thakolkaran2025can}
Thakolkaran, P., Guo, Y., Saini, S., Peirlinck, M., Alheit, B., \& Kumar, S. (2025).
\newblock Can {KAN} {CAN}s? {I}nput-convex {Kolmogorov-Arnold networks (KANs)} as hyperelastic constitutive artificial neural networks ({CAN}s).
\newblock {\em Computer Methods in Applied Mechanics and Engineering}, 443, 118089.

\bibitem[Uscidda \& Cuturi, 2023]{uscidda2023monge}
Uscidda, T. \& Cuturi, M. (2023).
\newblock The {Monge} gap: {A} regularizer to learn all transport maps.
\newblock In {\em International Conference on Machine Learning}  \!\!, pages 34709--34733.: PMLR.

\bibitem[Villani, 2008]{villani2008optimal}
Villani, C. (2008).
\newblock {\em Optimal transport: old and new}, volume 338.
\newblock Springer.

\bibitem[Wang et~al., 2010]{wang2010optimal}
Wang, W., Ozolek, J.~A., Slep{\v{c}}ev, D., Lee, A.~B., Chen, C., \& Rohde, G.~K. (2010).
\newblock An optimal transportation approach for nuclear structure-based pathology.
\newblock {\em IEEE transactions on medical imaging}, 30(3), 621--631.

\bibitem[Warin, 2023]{warin2023groupmax}
Warin, X. (2023).
\newblock The {GroupMax} neural network approximation of convex functions.
\newblock {\em IEEE Transactions on Neural Networks and Learning Systems}, 35(8), 11608--11612.

\bibitem[Warin, 2024]{warin2024p1}
Warin, X. (2024).
\newblock {P1-KAN}: {An} effective {Kolmogorov-Arnold network} with application to hydraulic valley optimization.
\newblock {\em Preprint arXiv:2410.03801}.

\bibitem[Weed \& Bach, 2019]{weed2019sharp}
Weed, J. \& Bach, F. (2019).
\newblock Sharp asymptotic and finite-sample rates of convergence of empirical measures in wasserstein distance.
\newblock {\em Bernoulli}, 25(4A), 2620--2648.

\bibitem[Yarotsky, 2017]{yarotski2017}
Yarotsky, D. (2017).
\newblock Error bounds for approximations with deep {ReLU} networks.
\newblock {\em Neural Networks}, 94, 103 -- 114.

\end{thebibliography}


%
%
%
%
%
%
\newpage
\appendix
\onecolumn

\section*{Supplementary Material}
The supplementary material is organized as follows. \Cref{app:QuantitativeApprox} provides the multivariate extensions of the approximation bounds for the quadratic function $\bx \mapsto \|\bx\|_2^2$ on $[0,1]^d$ by ReLU ICNNs and HyCNNs, respectively. \Cref{app:proofs} collects all omitted proofs of the results stated in the main text and in \Cref{app:QuantitativeApprox}. \Cref{appendix_init} details the derivation of the initialization scheme for HyCNNs introduced in \Cref{sec:HyCNNs}. \Cref{app:additional_experiments} contains additional experimental results and implementation details (complementing \Cref{sec:experiments}), including visualizations of randomly initialized HyCNNs, further regression experiments, and additional results on neural OT map estimation. \Cref{app:single_cell} presents further details to neural OT based single-cell RNA-seq perturbation response prediction for the prepocessed 4i dataset \citep{bunne2023learning}.

\section{Quantitative Approximation of Multivariate Quadratic Functions}\label{app:QuantitativeApprox}

In this section we state the multivariate extensions of the approximation lower and upper bounds for approximating the quadratic function $\bx \mapsto \|\bx\|_2^2$ on $[0,1]^d$ by ReLU ICNNs and HyCNNs, respectively. The proofs are deferred to Appendix \ref{appendix_proof_multivariate}.

%

\begin{proposition}\label{prop:lowerBoundMultivariateICNN}
    Any (standard or leaky) ReLU ICNN $f_\theta\colon \RR^d \to \RR$ with $L$ hidden layers and $d_\ell$ neurons in layer $\ell$ satisfies the lower bound 
    \begin{align*}
        \int_{[0,1]^d} \big|f_\theta(\bx)-\|\bx\|_2^2 \big| \, d\bx &\geq \frac{1}{16(d_1 + 2 \sum_{\ell = 2}^L d_\ell)^2} \quad \text{and}\\
        \sup_{\bx\in [0,1]^d}|f_\theta(\bx)-\|\bx\|_2^2| &\geq \frac{d}{8 (d_1 + 2 \sum_{\ell = 2}^L d_\ell)^2}.
    \end{align*}
\end{proposition}

\begin{proposition}\label{thm:quadratic_approximation_multi}
	For any $d, L, m\in \NN$, with $m\geq 3$ there exists a HyCNN $f\colon \RR^d \to \RR$ with $L$ hidden layers and $m$ neurons per layer, %
    such that 
     \begin{align*}
        \sup_{\bx\in [0,1]^d} \big|f(\bx) - \|\bx\|_2^2\big| \leq \frac{d}{8} \inf_{p,q \in \NN: pq \geq d}  \left\lfloor \frac{m-1}{q}-1 \right\rfloor^{-2\lfloor L/p \rfloor}.
     \end{align*}
\end{proposition}

The key conceptual insights are that also in high-dimensional settings, HyCNNs can approximate the quadratic function $\bx \mapsto \|\bx\|_2^2$ with an error that decays exponentially in the depth and polynomially in the width, whereas (standard or leaky) ReLU ICNNs can only achieve a polynomial decay in the width and no decay in the depth.
Indeed, combining Theorem 11 of \citet{liang2017why} with the last inclusion in \eqref{eq.84gr} shows that the exponential decay with respect to the depth is optimal, for both ReLU networks and HyCNNs.

\section{Omitted Proofs}\label{app:proofs}

\subsection{Technical lemmas}

\begin{lemma} \label{lemma_comp_convexnondecre}
    Let $\overline \sigma \colon \RR^2 \to \RR$ be convex and componentwise non-decreasing. 
    If $f: \mathbb{R}^d \to \mathbb{R}$ and $g: \mathbb{R}^d \to \mathbb{R}$ are convex functions, then
    $h : \bx \mapsto \overline \sigma(f(\bx), g(\bx))$ is convex.
\end{lemma}
\begin{proof}
    For any $\bx_1, \bx_2 \in \RR^d$ and $t \in [0,1]$, we have
    \[
        f\big( t\bx_1 + (1-t)\bx_2\big) \leq t f(\bx_1) + (1-t) f(\bx_2), \quad 
        g\big( t\bx_1 + (1-t)\bx_2\big) \leq t g(\bx_1) + (1-t) g(\bx_2).
    \]
    Hence, by the assumptions imposed on $\overline \sigma$ we get
    \begin{align*}
        h\big( t\bx_1 + (1-t)\bx_2  \big) 
        &= \overline \sigma\Big(f\big( t\bx_1 + (1-t)\bx_2  \big), \, g\big( t\bx_1 + (1-t)\bx_2  \big)\Big)\\
        & \leq t \overline \sigma\big(f(\bx_1), g(\bx_1)\big) + (1-t) \overline \sigma\big(f(\bx_2), g(\bx_2)\big)\\
        & = t h(\bx_1) + (1-t) h(\bx_2).
    \end{align*}
    The second inequality follows directly from the fact that $h$ is a convex function as stated in the Lemma.
\end{proof}

The composition of two convex functions is not necessarily again a convex function. The same holds for the composition of two HyCNNs. The next result reveals that specific compositions of HyCNNs can still be represented by deeper HyCNNs.

\begin{lemma}[Composition of two HyCNNs]
\label{lemma_hycnn_comp}
    Consider a HyCNN $g \colon \RR^{d} \to \RR^{p} $ with $L_1$ hidden layers and $(d_1, \dots, d_{L_1})$ neurons per layer,  specified for $\ell \in \{0, \dots, L_1-1\}$ by
\begin{align*}
    g(\bx) \coloneqq V_{L_1}\bz_{L_1} + W_{L_1} \bx + \bb_{L_1}, \qquad \bz_{\ell+1} &:= \overline\sigma\left((V_\ell^{k} \bz_{\ell} + W_{\ell}^{k} \bx + \bb_{\ell}^{k})_{k\in \{1,2\}}\right)
\end{align*}
with $\bz_0 \coloneqq \mathbf{0}_d$.
    In addition, consider another HyCNN $h \colon \RR^{p+d} \to \RR^{q} $ with $L_2$ hidden layers and $(p_{1}, \dots, p_{L_2})$ neurons per layer,  specified for $\ell \in \{0, \dots, L_2-1\}$ by 
    %
%
%
%
\begin{align*}
    h(\by,\bx) \coloneqq H_{L_2}\bu_{L_2} + M_{L_2} \by + N_{L_2} \bx + \bc_{L_2}, \qquad \bu_{\ell+1} &:= \overline\sigma\left((H_\ell^{k} \bu_{\ell} + M_\ell^{k} \by + N_\ell^{k} \bx + \bc_{\ell}^{k})_{k\in \{1,2\}}\right)
\end{align*}
with $\bu_0 \coloneqq \mathbf{0}_p$.
If the matrices $\{M_{\ell}^{1}, M_{\ell}^{2}\}_{\ell =0}^{L_2 - 1}$ and
$M_{L_2}$ are all componentwise non-negative, 
then there exits a HyCNN $f \colon \RR^{d} \to \RR^{q} $ with $L_1+L_2$ hidden layers and $(d_1, \dots, d_{L_1}, p_{1}+p, \ldots, p_{L_2}+p)$ neurons per layer such that $f(\bx) = h(g(\bx),\bx)$ for all $\bx\in \RR^d$.
\end{lemma}
\begin{proof}
    We construct the HyCNN $f$ with weight matrices $\{R_\ell^k\}$, skip connection matrices $\{S_\ell^k\}$ and bias vectors $\{\bd_\ell^k\}$ as follows. The first $L_1$ hidden layers exactly match that of $g$, i.e., for $\ell \in \{0, \dots, L_1-1\}$ and $k \in \{1,2\}$, we set $R_\ell^k = V_\ell^k$, $S_\ell^k = W_\ell^k$ and $\bd_\ell^k = \bb_\ell^k$. Choosing the matrices and bias vectors identical  ensures that the output of the $L_1$-th hidden layer of $f$ is exactly $\bz_{L_1}$.

    For the $(L_1+\ell)$-th hidden layer with $\ell\in \{1, \dots, L_2\}$, we consider $p_{\ell}+p$ neurons. Concretely, for $k \in \{1,2\}$, we set 
    \[R_{L_1}^k = \begin{bmatrix}
         M_0^{k} V_{L_1}\\
        V_{L_1}
        \end{bmatrix}, \qquad
    S_{L_1}^k = \begin{bmatrix}
        M_0^{k} W_{L_1} + N_0^{k}   \\ W_{L_1}
         \end{bmatrix} , \qquad 
    \bd_{L_1}^k = 
    \begin{bmatrix}
        M_0^{k} \bb_{L_1} + \bc_0^{k} \\
        \bb_{L_1}
    \end{bmatrix}.\]
    Since the matrices $R_{L_1}^k$ are constructed from $M_0^k$ and $V_{L_1}$, and $V_{L_1}$ is non-negative, it follows that $R_{L_1}^k$ is non-negative regardless of the signs of $M_0^k$.
    By construction, the output of $f$ is exactly $h \circ g$.
\end{proof}

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

\subsection{Proofs for limited expressivity of ICNNs}

\begin{proof}[Proof of \Cref{prop:piecewise_linear_icnn}]
Consider an ICNN architecture with $L$ hidden layers. For $\ell = 1$, each hidden neuron $z_{1,j} = \sigma(W_1^{j} x + b_1^{j})$ is piecewise-affine with at most one discontinuity. Thus $|\calK_1| \leq d_1$.

For the induction step, assume $|\calK_{\ell-1}| \leq \sum_{i=1}^{\ell-1} 2d_i$. For layer $\ell$, each neuron $z_{\ell,j} = \sigma(V_{\ell-1}^{j} \bz_{\ell-1} + W_\ell^{j} x + b_\ell^{j})$ is a convex function. Since a convex function can have at most one root, the number of new discontinuities is $d_\ell$. Thus $|\calK_\ell| \leq |\calK_{\ell-1}| + d_\ell$. By induction, $|\calK_L| \leq \sum_{\ell=1}^L d_\ell$.
\end{proof}

The proof of \Cref{thm:lowerBoundPiecewiseLinear} is based on the following bound on approximation of quadratic functions by affine functions.

\begin{lemma}\label{lem:bestline_lp}
    For any real numbers $a<b$, 
\begin{align*}
\inf_{\ell\ \text{\em affine}}\ \int_a^b \big|x^2-\ell(x)\big| \, dx &= \frac{(b-a)^{3}}{16},\\
\inf_{\ell\ \text{\em affine}}\ \sup_{x\in[a,b]}|x^2-\ell(x)| &= \frac{(b-a)^2}{8}.
\end{align*}
\end{lemma}

The second claim of the previous result has been previously shown in Lemma 4.5 of \citealt{eckle2019comparison}. For the sake of completeness, we include a proof below. 

\begin{proof}
Substitute $t:=(x-m)/h \in [-1,1]$ with $m=(a+b)/2$ and $h=(b-a)/2.$ 
\begin{align}\label{eq:reduce}
\inf_{\ell\ \text{\em affine}}\ \int_a^b \big|x^2-\ell(x)\big| \, dx =
h^{3} \inf_{c,d}\ \int_{-1}^1 |t^2-ct-d| \, dt.
\end{align}
Because the function $t^2$ is symmetric on $[-1,1]$, any affine approximation $\ell(t) = ct+d$ must have $c=1$ to minimize the integral. Thus, the infimum is attained for $c=1$, and
\begin{align*}
\inf_{c,d}\ \int_{-1}^1 |t^2-ct-d| \, dt
=\inf_{d}\ \int_{-1}^1 |t^2-t-d| \, dt = \frac{1}{2}.
\end{align*}
Combined with \eqref{eq:reduce}, we obtain the result.
\end{proof}

\begin{proof}[Proof of Theorem \ref{thm:lowerBoundPiecewiseLinear}]
Let $g\in\calG_k$. Then there exists a partition $0=t_0<t_1<\cdots<t_m=1$ with $m\le k$ such that $g$ is affine on each $[t_{k-1},t_k]$. Let $L_k:=t_k-t_{k-1}$ and $L_{\max}:=\max_k L_k$. Since $\sum_k L_k=1$, we have $L_{\max}\ge 1/m\ge 1/k$.
On the interval $I=[t_{j-1},t_j]$ with $L_j=L_{\max}$ the function $g$ is affine, hence by Lemma~\ref{lem:bestline_lp}
\begin{align*}
\sup_{x\in [0,1]}|g(x)-x^2| \geq \sup_{x\in I}|g(x)-x^2|
\;\ge\; \inf_{\ell\ \text{affine}}\ \sup_{x\in I}|\ell(x)-x^2|
= \frac{L_{\max}^2}{8}
\;\ge\; \frac{1}{8k^2}.
\end{align*}
Since this bound holds for the supremum norm, the assertion for the $L^1$ norm follows immediately as the $L^1$ norm is always bounded by the supremum norm.
\end{proof}

\begin{remark}[Lower bounds for higher order monomials]
%
 For higher order monomials $x\in [0,1]\mapsto x^n$ with $n=3,\ldots,$ similar lower bounds as for the quadratic function hold, though the proof is more involved. E.g.,  \citet[Equation (6.17)]{mcclure1975nonlinear} asserts for $n\geq 2$ that $$\liminf_{k\to \infty} k^2\inf_{g\in \calG_k}\smash{\int_{0}^{1}}|g(x) - x^n| \, dx\geq C_n>0$$ where $\calG_k$ is the set of real-valued piecewise-affine, convex functions and $C_n$ only depends on $n$. %
\end{remark}

\subsection{Proof for approximation of quadratic functions with HyCNNs}

In this section, we provide the proof of Theorem \ref{thm:quadratic_approximation}.
We write $x_+ \coloneq \max(x,0)$. 
%

\begin{lemma}\label{lemma_sq_approx_pc}
    For any $m=1,2,\ldots,$
    $$\sup_{x \in [0,1]} \left|\left(- \frac{1}{8 m^2} + \frac{x}{m} + \frac{2}{m}\sum_{k=1}^{m-1} \Big(x - \frac{k}{m}\Big)_+ \right) - x^2  \right|\leq \frac{1}{8m^2}.$$
\end{lemma}
\begin{proof}
    We fix $j \in [m]$. For any $x \in [\tfrac{j-1}{m}, \tfrac{j}{m}]$,
    observe that the sum $\sum_{k=1}^{m-1} (x - k/m)_+$ vanishes because $x$ is in the first interval. 
    Hence, the expression simplifies to:
\begin{align*}
- \frac{1}{8 m^2} + \frac{x}{m} = \frac{2j-1}{m}x - \frac{j(j-1)}{m^2} - \frac{1}{8m^2}.
\end{align*}
Since this holds for all $j$, the supremum is bounded by $1/8m^2$.
\end{proof}

%

\begin{proof}[Proof of Theorem \ref{thm:quadratic_approximation}]
We define $D_{\ell} := \prod_{i=1}^{\ell} d_{i}$. The construction is done by induction. 
For the base case $\ell=1$, we construct $d_1$ neurons $z_{1,j}(x) = (x - j/d_1)_+$. 
For the induction step, we assume $u_\ell(x)$ is a non-negative affine combination of $\bz_\ell$. 
We define $z_{\ell+1, j}(x) = \phi_\ell(x) + \psi_\ell(x)$ for all $j$. 
Since $\phi_\ell$ and $\psi_\ell$ are non-negative combinations of $\bz_\ell$, then $z_{\ell+1, j}$ is also a non-negative combination. 
Thus, by induction, the final output $f(x)$ is a linear function of $x$. 
By Lemma \ref{lemma_sq_approx_pc}, the error is bounded.
\end{proof}

\begin{remark}
\label{rem.74f}
    %
    From \eqref{tmp_15}, \eqref{tmp_14} and \eqref{tmp_13},  we observe that not only elements of $\{V_\ell^{1}\}_{\ell=0}^{L-1}$ and $V_L$, but also
    $\{\bw_\ell^{1}\}_{\ell=0}^{L-1}$ and $w_L$ in the network are non-negative.
    This property is exploited in the approximation of monomial functions in Appendix~\ref{appendix_monomial}. 
\end{remark}

\begin{proof}[Proof of Lemma \ref{lemma_z_equal}]
    We fix $\ell \in \NN$, $j \in [d_{\ell+1}-1]$. 
    Further, we write $\Delta \coloneq \Delta_{\ell} = a_\ell - b \geq 0$ and  
\begin{align*}
\mathcal{L}(x):= - \frac{\Delta j}{2 D_{\ell} d_{\ell+1}} + \frac{\Delta}{2}\,x , \qquad 
F(x):=\max\Bigl(\phi_\ell(x),\,\mathcal{L}(x)+\psi_\ell(x)\Bigr).
\end{align*}
\emph{Step 1: Slopes.}
On each interval $I_k$, the slope of $t(x) = \mathcal{L}(x) + \psi_\ell(x) - \phi_\ell(x)$ is constant. 
\emph{Step 2: Jump heights.}
At each kink $x_k$, the jump height of $F'$ is $\Delta/2$. 
Since all jump heights are positive, $F$ is convex and the hinge representation follows.
\end{proof}

\begin{proof}[Proof of Lemma \ref{lemma_u_affine}]
We define constants $r_j$ as in \eqref{tmp_10}. To show that $u_{\ell+1}$ is a non-negative affine combination of $z_{\ell+1,j}$, we observe that the sum $\sum r_j z_{\ell+1,j}$ results in a piecewise linear function with $D_{\ell+1}$ pieces. Since Lemma \ref{lemma_u_affine} states that $u_{\ell+1}$ is the unique function represented by such a combination, the identity $\sum r_j z_{\ell+1,j} = u_{\ell+1}$ must hold. Thus, the coefficients $r_j$ are non-negative and the lemma is proved.
\end{proof}

We also present an alternative theorem and proof below, which is more accessible.
The network construction below is similar to that of original proof for ReLU networks (e.g., \citet{yarotski2017}),
and highlights the key idea behind the exponential approximation rate.

\begin{lemma} \label{lemma_comp_multiple_bump}
Let $\psi:[0,1]\to [0,1]$ be the function $\psi(u)=|2u-1|$ and define $\psi^{\circ k}=\psi \circ \ldots \circ \psi$ as the $k$-fold composition of $\psi.$ Then, 
\begin{itemize}
    \item[(i)] $\psi^{\circ k}+(1-\psi)^{\circ k}=1,$
    \item[(ii)] for a real number $u$ denote by $\{u\} \coloneqq u - \lfloor u \rfloor \in [0,1)$ the fractional part. For any $y\in [0,1],$ and any $k=1,2,\ldots,$ $$\psi^{\circ k}(y)=\psi\big(\{2^{k-1}y\}\big),$$ 
    \item[(iii)] for any $L=1,2,\ldots,$ the function $$x\mapsto \sum_{k=1}^L 4^{-k} \big(1-\psi^{\circ k}(x)\big)$$ interpolates $x\mapsto x(1-x)$ at the point $\ell 2^{-L}$ and for any $\ell=0,\ldots, 2^L,$
    and is affine on the interval $[\ell 2^{-L}, (\ell +1 )2^{-L}]$ for any $\ell = 0,\ldots, 2^L - 1$,
    \item[(iv)] for any $L=1,2,\ldots$
\begin{align*}
\sup_{x\in [0,1]} \, \Big|x+\sum_{k=1}^L 4^{-k}\big(\psi^{\circ k}(x)-1\big) - 2^{-2L-3} 
-x^2\Big|= 2^{-2L-3}. 
\end{align*}
\end{itemize}
\end{lemma}

Before we give the proof of the lemma, we state the main result. 

\begin{theorem}[Special case of Theorem \ref{thm:quadratic_approximation}]
    For any $L\in \NN$, there exists a HyCNN $h \colon \RR\to \RR$ with $L$ hidden layers and $2$ neurons per layer,  
    such that 
     \begin{align*}
       \int_{[0,1]^d}|h_\theta(x)- x^2| \, dx\leq  \sup_{x\in [0,1]}|h_\theta(x) - x^2| = 2^{-2L-3}.
     \end{align*}
\end{theorem}
\begin{proof}
For real numbers $u,v,$ we have $2\max(u,v)=u+v+|u-v|.$ Therefore, a layer of the form
\[\bz\mapsto  %
    \max\big(V^{1} \bz + W^{1} \bx + \bb^{1}, V^{2} \bz + W^{2} \bx + \bb^{2}\big)\]
with $V^1, V^2$ entrywise non-negative, is equivalent to the existence of matrices $A, B, D, E$ and vectors $\ba, \bb$ such that the absolute value of every entry in $D$ is upper bounded by the corresponding entry of $A$ (implying that $A-D$ and $A+D$ are entrywise non-negative) and 
\begin{align}
    \bz\mapsto 
A\bz +B\bx +\ba + \big|D\bz+E\bx+\bb\big|,
\label{eq.layer_reform}
\end{align}
where $|\cdot|$ is the componentwise absolute value. Let $\psi:[0,1]\to [0,1]$ be the function $\psi(u)=|2u-1|$ and define $\psi^{\circ k}=\psi \circ \ldots \circ \psi$ as the $k$-fold composition of $\psi.$ For any $m=1,2,\ldots$ we now show that there exists a network with $L$ hidden layers, one input neuron, one output neuron, and two neurons in each of the hidden layers, 
such that the $m$-th hidden layer computes 
%
\[
\left(
\begin{array}{c}
2^{-2m}\psi^{\circ m}(x)+\sum_{k=1}^m 2^{-2k}\psi^{\circ k}(x)    \\
\sum_{k=1}^{m-1} 2^{-2k}\psi^{\circ k}(x)
\end{array}\right).
\]
%
Then, we can average the two activations in the output layer and add the term $x-\sum_{k=1}^L 2^{-2k}  - 2^{-2L-3}$ to get a network computing 
$$x+\sum_{k=1}^L 2^{-2k}\big(\psi^{\circ k}(x)-1\big) - 2^{-2L-3},$$
and get the assertion by applying Lemma~\ref{lemma_comp_multiple_bump} (iv).

The case $m=1$ follows directly from the form \eqref{eq.layer_reform} with $A=B=\ba=D=0,$ $E=1/2,$ $\bb=-1/4.$ For the induction step from $m$ to $m+1$, take $B=E=\ba=(0,0)^\top,$ 
\[
A= \left(
\begin{array}{ccc}
  1/2   & 1/2  \\
 1/2   & 1/2 
\end{array}\right), \quad  
D= 
\left(
\begin{array}{cc}
1/2   & -1/2  \\
 0  &  0
\end{array}\right)
, 
\quad  \bb = \left(\begin{array}{c}
-2^{-2m-1} \\
     0 
\end{array}\right).
\]
The choice satisfies the constraint that the entries in $D$ are in absolute value dominated by the corresponding entries in $A.$ Observe that
$$
2^{-2m-1}\psi^{\circ (m+1)}(x)
= 2^{-2m-1} |2\psi^{\circ m}(x) -1|
= |2^{-2m} \psi^{\circ m}(x) -2^{-2m-1} |. 
$$
If $\bz_m$ where the activations of the previous layer and using the induction hypothesis, $D\bz_m=2^{-2m}\psi^{\circ m}$ and $$A\bz_m+|D\bz_m+\bb|= \sum_{k=1}^m 2^{-2k}\psi^{\circ k}(x)\left(
\begin{array}{c}
     1  \\
     1 
\end{array}
\right)+  2^{-2m-2}\psi^{\circ (m+1)}(x)
\left(
\begin{array}{c}
     2  \\
     0 
\end{array}
\right)$$ proving the induction hypothesis.

\end{proof}

\begin{proof}[Proof of Lemma~\ref{lemma_comp_multiple_bump}] \textit{(i):}
We prove $\psi^{\circ k}+(1-\psi)^{\circ k}=1$ using induction on $k.$ The formula holds for $k=1.$ To go from $k$ to $k+1,$ observe that by $\psi^{\circ (k+1)}=\psi^{\circ k}\circ \psi$, $(1-\psi)^{\circ (k+1)}=(1-\psi)^{\circ k}\circ (1-\psi)$, the induction hypothesis, and the fact that $\psi$ is symmetric around $1/2$ in the sense that $\psi(u)=\psi(1-u),$ thus, $\psi\circ \psi=\psi\circ (1-\psi),$ we obtain $\psi^{\circ (k+1)}+(1-\psi)^{\circ (k+1)}= \psi^{\circ k}\circ \psi + 1-  \psi^{\circ k}\circ (1-\psi)=1,$ proving the induction step. 

\textit{(ii):} The formula holds trivially for $k=1.$ 

We now prove it for $k=2:$ Note that $y=\{2y\}/2$ if $0\leq y< 1/2$ and $y=1/2+\{2y\}/2$ if $1/2\leq y< 1.$ Therefore, $\psi(y)= |2 y - 1 | = |\{2y\}-1| = 1 - \{2y\} $ if $0\leq y<1/2$ and $\psi(y)= |2 y - 1 | = \{2y\}$ if $1/2\leq y <1.$
Since $\psi(u)=\psi(1-u)$ for all real numbers $u,$ we find $\psi\circ \psi(y)=\psi(\{2y\})$ for all $0\leq y<1.$ For $y=1$, the formula holds since $\psi(0)=\psi(1)=1.$ 

To prove $\psi^{\circ k}(y)=\psi(\{2^{k-1}y\})$ for general $k$, it is enough to show the induction step $k\to k+1.$ Using the induction hypothesis and the case $k=2$ proved above, $\psi^{\circ (k+1)}(y)=\psi(\psi^{\circ k}(y))=\psi\circ \psi(\{2^{k-1}y\})=\psi(\{2\{2^{k-1}y\}\})=\psi(\{2^ky\}).$

\textit{(iii):} By (ii), $\psi^{\circ k}(y)=\psi(\{2^{k-1}y\}).$ Since $\psi(x)=|2x-1|$ is affine on $[0,1/2]$ and $[1/2,1],$ it follows that  $\psi^{\circ k}$ is piecewise-affine on the intervals $[\ell/2^k,(\ell+1)/2^k]$ with endpoints $\psi^{\circ k}(\ell/2^k) = \psi(1/2) =0$ if $\ell$ is odd and $\psi^{\circ k}(\ell/2^k) = \psi(0)= 1$ if $\ell$ is even. 

For convenience, write $g(x) = x(1-x).$ In the next step, we show that for any $m \geq 1$ and any $\ell =0,1, \ldots, 2^L,$
\begin{align*}
	g(\ell 2^{-L}) = \sum_{k=1}^L 4^{-k} \big(1-\psi^{\circ k}(\ell 2^{-L})\big).
\end{align*}
We prove this by induction over $L.$ For $L=1$ the result can be checked directly. For the inductive step, suppose that the claim holds for $L.$ If $\ell$ is even we use that $\psi^{\circ (L+1)}(\ell 2^{-L-1})=1$ to obtain that $g(\ell 2^{-L-1}) = \sum_{k=1}^L 4^{-k}(1-\psi^{\circ k}(\ell 2^{-L-1})) = \sum_{k=1}^{L+1} 4^{-k}(1-\psi^{\circ k}(\ell 2^{-L-1})).$ It thus remains to consider $\ell$ odd. Recall that $x\mapsto \sum_{k=1}^L 4^{-k} (1-\psi^{\circ k}(x))$ is affine on $[(\ell-1)2^{-L-1}, (\ell+1)2^{-L-1}]$ and observe that for any real $t,$
\begin{align*}
	g(x) = t^2 + \frac{g(x-t)+g(x+t)}{2}.
\end{align*}
For odd $\ell,$ choose $x =\ell 2^{-L-1}$ and $t=2^{-L-1}.$ Applying the identity and $\psi^{\circ (L+1)}(\ell 2^{-L-1}) =0$ yield
\begin{align*}
	g(\ell 2^{-L-1})  
&= 2^{-2L-2} + \frac{g\big((\ell-1)2^{-L-1}\big) + g\big((\ell+1)2^{-L-1}\big)}{2}  \\
&= 4^{-L-1}+\frac{1}{2}\bigg(
\sum_{k=1}^L 4^{-k}\Big(1-\psi^{\circ k}\big((\ell-1) 2^{-L-1}\big)\Big)
+
\sum_{k=1}^L 4^{-k}\Big(1-\psi^{\circ k}\big((\ell+1) 2^{-L-1}\big)\Big)
\bigg) \\
&= 4^{-L-1}+\sum_{k=1}^L 4^{-k}\big(1-\psi^{\circ k}(\ell 2^{-L-1})\big) \\
    &= \sum_{k=1}^{L+1} 4^{-k} \big(1-\psi^{\circ k}(\ell 2^{-L-1})\big).
\end{align*}
This completes the inductive step and proves assertion \textit{(iii)}.

\textit{(iv):} For a quadratic function $h$ with $h(a)=h(b)=0$ and $K=h''(a)=h''(b),$ one has that $h(x)=\tfrac K2 (x-a)(x-b).$ Since $g''(x)=-2,$ for any $\ell =0,\ldots, 2^L-1,$ and any $x\in [\ell 2^{-L}, (\ell+1) 2^{-L}],$ 
\begin{align}
	g(x) - \sum_{k=1}^L 4^{-k} \big(1-\psi^{\circ k}(x)\big) 
	&= -\big(x - (\ell+1)2^{-L}\big) \big(x-\ell2^{-L}\big) = \big((\ell+1)2^{-L} -x\big) \big(x-\ell2^{-L}\big).
\end{align}
For any $x\in [\ell 2^{-L}, (\ell+1) 2^{-L}],$
\begin{align*}
   0 \leq \Big(\frac{\ell+1}{2^{L}} -x\Big) \Big(x-\frac{\ell}{2^{L}}\Big) \leq
   \Big(\frac{\ell+1}{2^{L}} -\frac{\ell+1/2}{2^{L}}\Big) \Big(\frac{\ell+1/2}{2^{L}}-\frac{\ell}{2^{L}}\Big)= 2^{-2L-2}.
\end{align*}
The second inequality becomes an equality for the interval midpoint $x=(\ell+1/2)2^{-L}.$ This shows that 
\begin{align*}
    \sup_{x\in [0,1]} \, \Big|g(x) - \sum_{k=1}^L 4^{-k} \big(1-\psi^{\circ k}(x)\big) -2^{-2L-3}\Big|=2^{-2L-3}.
\end{align*}
The assertion follows using that $g(x)=x(1-x)=x-x^2.$

%
%
%
%
%
%

\end{proof}

\subsection{Proofs for monomial functions}
\label{appendix_monomial}

The following two lemmas state how HyCNNs can approximate the functional operators $\calD_0$ and $\calD_1$, defined by
$$\calD_0 [f](x) := f^2(x), \qquad \calD_1 [f](x) := f^2(x)/x.$$ 
These operators are crucially used in the proof of Theorem~\ref{thm_monomial}.
Approximating $\calD_0$ is straightforward from Theorem~\ref{thm:quadratic_approximation}, whereas approximating $\calD_1$ is a non-trivial problem. 

\begin{lemma}\label{lem_approx_operator_0}
Consider a HyCNN $g \colon \RR\to \RR$ with $L'$ hidden layers and $m'$ neurons per hidden layer.
Assume that $0 \leq g(x) \leq x$ for every $x \in [0,1]$.
Then, for any $L \in \NN$ and $m \in 2 \NN$, 
\begin{enumerate}
    \item [(i)] there exists a HyCNN $\tilde g_0 \colon \RR\to \RR$ with $L' + L$ hidden layers and $\max(m', m+1)$ neurons per hidden layer such that $0 \leq \tilde g_0(x) \leq x$ for every $x \in [0,1]$ and
$$\sup_{x \in [0,1]} \big|\tilde g_0(x) - \calD_0 [g](x) \big| \leq \frac{1}{4 m^{2L}}.$$
    \item[(ii)] there exists a HyCNN $\tilde g_1 \colon \RR\to \RR$ with $L' + L$ hidden layers and $\max(m', m+1)$ neurons per hidden layer such that $0 \leq \tilde g_1(x) \leq x$ for every $x \in [0,1]$ and 
$$\sup_{x \in [0,1]} \big|\tilde g_1(x) - \calD_1 [g](x) \big| \leq \frac{1}{4 m^{2L}}.$$
\end{enumerate}

\end{lemma}

To prove this lemma, we need the following two key results.
First, we modify our network to approximate the quadratic function, in order to ensure that the \textit{skip-connection weight matrices}, i.e., the matrices
$\{W_{\ell}^1, W_{\ell}^2\}_{\ell =0}^{L-1}$ and $W_{L}$ in \eqref{eq:HyCNN}, are element-wise non-negative. This is relevant for proving \Cref{lem_approx_operator_0}$(i)$, concretely in order to ensure composability of HyCNNs according to \Cref{lemma_comp_convexnondecre}. 
%
%
%
%
%
%
%
%
%

\begin{lemma}\label{lemma_positive_qudratic}
    For any $L \in \NN$ and $m \in 2 \NN$, there exists a HyCNN $f : \RR \to \RR$ with $L$ hidden layers and $m$ neurons per hidden layer such that
$$\sup_{x \in [0,1]} \big|f(x) - x^2 \big| \leq \frac{1}{4 m^{2L}}$$
and $0 \leq f(x) \leq x$ for every $x \in [0,1]$.
Moreover, all the skip-connection weight matrices of $f$ are element-wise non-negative. 
\end{lemma}
\begin{proof}
    We define $M \coloneqq m^{L}$.
    By adding $(8M^2)^{-1}$ to \eqref{tmp_16} in the proof of Theorem~\ref{thm:quadratic_approximation}, we can construct a HyCNN $f: \RR \to \RR$ with $L$ hidden layers and $m$ neurons per hidden layer such that
    \[
    f(x) = \frac{x}{M} + \frac{2}{M}\sum_{k=1}^{M-1} \left(x - \frac{k}{M}\right)_+,
    \]
    and all the skip-connection weight matrices of $f$ are element-wise non-negative (See \Cref{rem.74f}). 
    By Lemma~\ref{lemma_sq_approx_pc}, we obtain
    $$\sup_{x \in [0,1]} |f(x)-x^2| \leq (8M^2)^{-1} + \sup_{x \in [0,1]} \left|-(8M^2)^{-1}+h(x)-x^2\right| \leq (4M^2)^{-1} = \frac{1}{4m^{2L}}.$$
    Noticing that $f(0)=0$ and 
    $$f(1) = \frac{1}{M} + \frac{2(M-1)}{M} - \frac{M(M-1)}{M^2} = 1.$$ 
    Since $f$ is non-decreasing and convex, we obtain the remained assertion by
    \[
    0 \leq f(x) \leq (1-x)f(0) + x f(1) = x.
    \]
\end{proof}

The next lemma serves as a crucial tool to prove Lemma \ref{lem_approx_operator_0}(ii). 
\begin{lemma}\label{lem:uy_y_yhu}
Consider a HyCNN $h \colon \RR^d \to \RR$ with $L$ hidden layers and $m$ neurons per hidden layer,  specified for $\ell \in \{0, \dots, L-1\}$ by
\begin{align*}
    h(\bx) = \bv_L^{\top} \bz_L(\bx) + \bw_L^{\top} \bx + b_L, \quad
\bz_{\ell+1}(\bx) = \max_{k\in \{1,2\}}\left(V_\ell^k \bz_{\ell}(\bx) + W_{\ell}^k \bx  + \bb_{\ell}^k\right), \quad
\bz_{0}(\bx)=0.
\end{align*}
For $\bx_1 \in \RR^d$ and $x_2 \in \RR$,
define $\tilde h (\bx_1, x_2)$ by 
\begin{equation}\label{tmp_17}
\begin{aligned}
\tilde h(\bx_1, x_2) &\coloneqq \bv_L^{\top} \tilde \bz_L(\bx_1, x_2) + \bw_L^{\top} \bx_1 + b_L x_2,\\
\tilde \bz_{\ell+1}(\bx_1, x_2) &\coloneqq 
\max_{k\in \{1,2\}}\left(V_\ell^k \tilde \bz_{\ell}(\bx_1, x_2) + W_{\ell}^k \bx_1 + \bb_{\ell}^k x_2 \right).
\end{aligned}
\end{equation}    
with $\bz_{0}(\bx_1, x_2)=\mathbf{0}_{d+1}$.
Then, it follows that $\tilde h(\bu y, y) = y h (\bu)$ for any $\bu \in \RR^d$ and $y \geq 0$.
\end{lemma}
\begin{proof}
%
The claim follows from induction on the depth $\ell$. For $\ell = 0$, we have 
\begin{align*}
   \tilde  \bz_1(\bu y, y) &= \max_{k\in \{1,2\}}\left(W_{0}^k \bu y  + \bb_{0}^k y \right) \\
    &= y \max_{k\in \{1,2\}}  \left(W_{0}^k \bu  + \bb_{0}^k \right)  \\
    &= y \bz_1(\bu).
\end{align*}
Assuming that $\tilde \bz_\ell(\bu y, y) = y \bz_\ell(\bu)$ for some $\ell\in \{0, \dots, L-1\}$, we get 
\begin{align*}
    \tilde  \bz_{\ell+1}(\bu y, y) &= \max_{k\in \{1,2\}}\left(V_\ell^k \tilde \bz_{\ell}(\bu y, y) +W_{\ell}^k \bu y  + \bb_{\ell}^k y \right)  \\
    &= \max_{k\in \{1,2\}}  \left(y V_\ell^k \bz_{\ell}(\bu) + W_{\ell}^k \bu y  + \bb_{\ell}^k y\right)  \\
    &= y \max_{k\in \{1,2\}}  \left(V_\ell^k \bz_{\ell}(\bu) + W_{\ell}^k \bu  + \bb_{\ell}^k \right)  \\
    &= y \bz_{\ell+1}(x),
\end{align*}
which proves the induction step. Finally,
\begin{align*}
    \tilde h(\bu y, y) &= \bv_L^{\top} \tilde \bz_L(uy, y)  + \bw_L^{\top} \bu y + b_L y \\
    &= y V_L \bz_L(\bu) + \bw_L^{\top} \bu y + b_L y \\
    &= y h(\bu).\qedhere
\end{align*}
\end{proof}

%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%

\begin{proof}[Proof of Lemma~\ref{lem_approx_operator_0}]
{(i).}
    By Lemma~\ref{lemma_positive_qudratic}, we can construct a HyCNN $h: \RR \to \RR$ with $L$ hidden layers and $m$ neurons per hidden layer such that
    $$\sup_{x \in [0,1]} |h(x)-x^2| \leq \frac{1}{4 m^{2L}},$$
    $0 \leq h(x) \leq x$ for every $x \in [0,1]$, and 
    all the skip-connection weight matrices of $h$ are element-wise non-negative.
    By Lemma~\ref{lemma_hycnn_comp},
there exists a HyCNN $\tilde g_0: \RR \to \RR$ with $L' + L$ hidden layers and $\max(m', m+1)$ neurons per hidden layer such that $\tilde g_0(x) = h \circ g(x)$.
We obtain the upper bound of the approximation error by
\begin{align*}
    \sup_{x \in [0,1]} \big|\tilde g_0(x) - g^2(x) \big| 
    =
    \sup_{x \in [0,1]} \big| h \circ g(x) - g^2(x) \big|    
    &\leq 
    \sup_{z \in [0,1]} \big| h(z) -  z^2 \big|\\    
    &\leq 
    \frac{1}{4m^{2L}},
\end{align*}
provided that $0 \leq g(x) \leq 1$.
Finally, from 
$0 \leq h \circ g(x) \leq x$ for every $x \in [0,1]$, we get
$0 \leq \tilde g_0(x) \leq x$.

\medskip 

{(ii).}
    By Lemma~\ref{lemma_positive_qudratic}, we can construct a HyCNN $h: \RR \to \RR$ with $L$ hidden layers and $m$ neurons per hidden layer such that
    $$\sup_{x \in [0,1]} |h(x)-x^2| \leq \frac{1}{4 m^{2L}},$$
    $0 \leq h(x) \leq x$ for every $x \in [0,1]$, and 
    all the skip-connection weight matrices of $h$ are element-wise non-negative.
 
By applying Lemma~\ref{lem:uy_y_yhu} to the HyCNN $h$, 
we define a function $\tilde h \colon \RR^2 \to \RR$ by
\begin{align*}
\tilde h(x_1, x_2) &\coloneqq \bv_L^{\top} \tilde \bz_L(x_1, x_2) + w_L x_1 + b_L x_2,\\
\tilde \bz_{\ell+1}(x_1, x_2) &\coloneqq 
\max_{k\in \{1,2\}}\left(V_\ell^k \tilde \bz_{\ell}(x_1, x_2) + \bw_{\ell}^k x_1 + \bb_{\ell}^k x_2 \right)
\end{align*}
with $\tilde z_{0}(x_1, x_2)=0$, where the 
parameters
$\bv_{L}, w_{L}, \bb_{L}$, $\{V_\ell^1, \bw_{\ell}^1, \bb_{\ell}^1\}_{\ell=0}^{L-1}$ and $\{ V_\ell^2, \bw_{\ell}^2, \bb_{\ell}^2\}_{\ell=0}^{L-1}$ coincide with those of the HyCNN $h$.
Then, $\tilde h$ 
satisfies $\tilde h(uy, y) = y h (u)$ for any $u \in \RR$ and $y \geq 0$.     
By plugging in $u=g(x)/x$ and $y=x$, we get
$$\tilde h\big(g(x), x\big) = x h\big(g(x)/x\big), \qquad \forall x \in [0,1].
$$
All the $\bv_{L}, w_{L}$ and $\{V_\ell^1, \bw_{\ell}^1, V_\ell^2, \bw_{\ell}^2 \}_{\ell=0}^{L-1}$ of $h$ (and of $\tilde h$) are element-wise non-negative.
Therefore, we can apply
Lemma~\ref{lemma_hycnn_comp}
to obtain a HyCNN $\tilde g: \RR \to \RR$ with $L' + L$ hidden layers and $\max(m', m+1)$ neurons per hidden layer such that $\tilde g(x) = \tilde h(g(x), x).$
We obtain the upper bound of the approximation error by
\begin{align*}
    \sup_{x \in [0,1]} \big|\tilde g(x) - g^2(x)/x \big| 
    =
    \sup_{x \in [0,1]} \big|x h\big(g(x)/x\big) - x (g(x)/x)^2 \big|    
    &\leq 
    \sup_{x \in [0,1]} \big| h\big(g(x)/x\big) -  (g(x)/x)^2 \big|\\    
    &\leq 
    \frac{1}{4m^{2L}},
\end{align*}
provided that $0 \leq g(x)/x \leq 1$.
Finally, from 
$0 \leq h(g(x)/x) \leq 1$ for every $x \in [0,1]$, we get
$0 \leq \tilde g(x) \leq x$.
\end{proof}

%
%
%
%
%
%
%

\begin{proof}[Proof of Theorem~\ref{thm_monomial}]
    %
    %
    %
    %
    %
    %
    %
    For functions $f\colon \RR\to \RR$, define the operators
    $$\calD_0 [f](x) := f^2(x), \qquad \calD_1 [f](x) := f^2(x)/x.$$ 
    Further, let $\phi_m(x) = x^m$ for $m\in \NN$. 
%
%
%
%
    %
    We define $k \coloneqq \lceil \log_2(n)\rceil$ and 
    represent $2^k - n$ through its binary digits.
    Since $0 \leq 2^k - n \leq 2^{k-1}-1$, there exist $b_1, \ldots, b_{k-1}$ with $b_i \in \{0,1\}$ for $i=1,\ldots,k-1$ such that
    $$2^k - n = \sum_{i=1}^{k-1} b_i 2^{i-1}.$$  
    Set $b_k \coloneqq 0$. 
    Since 
    $\calD_{b}[\phi_m](x) = \phi_{2m-b}(x)$ for any $b \in \{0,1\}$ and $m \in \NN$, 
    we get
 \begin{align}
   \calD_{b_1} \circ \calD_{b_2} \circ \ldots \circ \calD_{b_{k-2}} \circ \calD_{b_{k-1}} \circ \calD_{b_k}[\phi_1](x) &=
   \calD_{b_1} \circ \calD_{b_2} \circ \ldots \circ \calD_{b_{k-2}} \circ \calD_{b_{k-1}}[\phi_2](x) \notag \\
   &= \phi_n(x)
   \label{tmp_18}
\end{align}
since
\begin{align*}
    \overbrace{2 \Big( \ldots 2\big(2(2}^{k-1 \text{ times}} \cdot \, 2 - b_{k-1}) - b_{k-2}\big)- b_{k-3} \ldots \Big) - b_1 =&
2^{k} - 2^{k-2} b_{k-1} - 2^{k-3} b_{k-2} - \ldots - b_1\\
=& 2^k - \sum_{i=1}^{k-1} b_i 2^{i-1} = n.
\end{align*}
%
%
%
%

We approximate the  composition with HyCNNs and track the approximation error using backward induction, starting with $k$ and then going down to $1.$ By Lemma~\ref{lem_approx_operator_0}, there exists a HyCNN $h_1: \RR \to \RR$ with $L$ hidden layers and $m$ neurons per hidden layer such that 
$$\sup_{x \in [0,1]} \big|h_1(x) - \calD_{b_k}[\phi_1](x) \big| 
=
\sup_{x \in [0,1]} \big|h_1(x) - x^2 \big| 
\leq \frac{1}{4 m^{2L}}$$
and $0 \leq h_1(x) \leq x$ for every $x \in [0,1]$.
Assume that for $i \in \{1,2,\ldots,k-1\}$, 
there exists a HyCNN $h_i: \RR \to \RR$ with $Li$ hidden layers and $m+1$ neurons per hidden layer such that 
$$\sup_{x \in [0,1]} \big|h_i(x) - \underbrace{\calD_{b_{k+1-i}} \circ \calD_{b_{k+2-i}} \circ \ldots \circ \calD_{b_k}}_{i \text{ times}}[\phi_1](x) \big|  
\leq \frac{2^i - 1}{4m^{2L}}$$
and $0 \leq h_i(x) \leq x$ for every $x \in [0,1]$.
For $x \in [0,1]$, we also have
$$0 \leq \calD_{b_{k+1-i}} \circ \ldots \circ \calD_{b_k}[\phi_1](x) \leq x.$$
By applying Lemma \ref{lem_approx_operator_0}-(i) for the case $b_{k-i}=0$ and Lemma \ref{lem_approx_operator_0}-(ii) 
for the case $b_{k-i}=1$, there exists a HyCNN 
$h_{i+1}: \RR \to \RR$ with $L(i+1)$ hidden layers and $m+1$ neurons per hidden layer such that 
\begin{align*}
    \sup_{x \in [0,1]} \big|h_{i+1}(x) - \calD_{b_{k-i}}[h_{i}](x) \big|  
\leq \frac{1}{4m^{2L}}
\end{align*}
and $0 \leq h_{i+1}(x) \leq x$ for every $x \in [0,1]$.
Using triangle inequality and the induction hypothesis,
\begin{align*}
    &\sup_{x \in [0,1]} \big|h_{i+1}(x) - \underbrace{\calD_{b_{k-i}} \circ \calD_{b_{k+1-i}} \circ \ldots \circ \calD_{b_k}}_{(i+1)\text{ - times}}[\phi_1](x) \big|\\
    &\leq 
    \sup_{x \in [0,1]} \big|h_{i+1}(x) - \calD_{b_{k-i}}[h_{i}](x) \big| 
    +
    \sup_{x \in [0,1]} \Big|\calD_{b_{k-i}}[h_{i}](x) - \calD_{b_{k-i}} \circ \calD_{b_{k+1-i}} \circ \ldots \circ \calD_{b_k}[\phi_1](x) \Big|\\   
    & = \sup_{x \in [0,1]} \big|h_{i+1}(x) - \calD_{b_{k-i}}[h_{i}](x) \big|
    +
    \sup_{x \in [0,1]} \left|\frac{h_{i}^2(x)}{x^{b_{k-i}}} - 
    \frac{\big(\calD_{b_{k+1-i}} \circ \ldots \circ \calD_{b_k}[\phi_1](x)\big)^2}{x^{b_{k-i}}}
    \right|\\
    & \leq \frac{1}{4m^{2L}} + 
    \sup_{x \in [0,1]} \frac{\left|\big(h_{i}(x) - \calD_{b_{k+1-i}} \circ \ldots \circ \calD_{b_k}[\phi_1](x)\big) 
    \big(h_{i}(x) + \calD_{b_{k+1-i}} \circ \ldots \circ \calD_{b_k}[\phi_1](x)\big)
    \right|}{x^{b_{k-i}}}\\
    & \leq \frac{1}{4m^{2L}} + 
    2 \cdot \frac{2^i - 1}{4m^{2L}} = \frac{2^{i+1} - 1}{4m^{2L}}.
\end{align*}
Hence, by backward induction on $i$, 
there exists a HyCNN 
$h_{k}: \RR \to \RR$ with $Lk$ hidden layers and $m+1$ neurons per hidden layer such that 
$$\sup_{x \in [0,1]} \big|h_k(x) - \calD_{b_{1}} \circ \calD_{b_{2}} \circ \ldots \circ \calD_{b_k}[\phi_1](x) \big|  
\leq \frac{2^k - 1}{4m^{2L}} < \frac{2^{k-2}}{m^{2L}} \leq \frac{n}{2 m^{2L}}.$$
The assertion then follows by recalling \eqref{tmp_18} and replacing $m$ by $m-1$. 
\end{proof}

\subsection{Proofs for multivariate quadratic
functions} \label{appendix_proof_multivariate}

\begin{proof}[Proof of \Cref{prop:lowerBoundMultivariateICNN}]
    Let $f \colon \RR^d \to \RR$ be a multivariate (standard or leaky) ReLU ICNN as in the claim. Then, by continuity of $f$ and $\|\cdot\|_2^2$, there exists $\bx' \in [0,1]^{d-1}$ such that
    \begin{align*}
         &\int_{[0,1]^d} \big|f(\bx)-\|\bx\|_2^2 \big| \, d\bx\geq  \int_0^1 \big|f(x, \bx') - x^2 - \|\bx'\|_2^2\big| \, dx
    \end{align*}
    In particular, the function $x\mapsto f(x, \bx')$ is a univariate (standard or leaky) ReLU ICNN with $L$ hidden layers and $d_\ell$ neurons in layer $\ell$. Hence, by \Cref{thm:lowerBoundPiecewiseLinear}, we have 
    \begin{align*}
        \int_0^1 \big|f(x, \bx') - x^2 - \|\bx'\|_2^2\big| \, dx &\geq \frac{1}{16(d_1 + 2 \sum_{\ell = 2}^L d_\ell)^2}.
    \end{align*}
    For the supremum norm, we infer upon denoting $\mathbf{1}_d = (1, \dots, 1)^{\top} \in \RR^d$ that 
    \begin{align*}
        \sup_{\bx\in [0,1]^d}\big|f(\bx)-\|\bx\|_2^2\big| \geq \sup_{t\in [0,1]}\big|f(t\mathbf{1}_d)-t^2 d\big| = d\sup_{t\in [0,1]}|d^{-1}f(t \mathbf{1}_d)-t^2|.
        %
    \end{align*}
    Since $t\mapsto d^{-1}f(t\mathbf{1})$ is a univariate (standard or leaky) ReLU ICNN on $[0,1]$ with $L$ hidden layers and $d_\ell$ neurons in layer $\ell$, the asserted lower bound also follows from \Cref{thm:lowerBoundPiecewiseLinear}. 
\end{proof}

\begin{proof}
[Proof of \Cref{thm:quadratic_approximation_multi}]

\begin{figure}[t]
  \centering  \includegraphics[width=.6\textwidth]{../figures/multivariate_qudratic.pdf}
  \caption{{Illustration of the proof of \Cref{thm:quadratic_approximation_multi}} for $d=8$ and $p=q=3$. 
    } \label{fig_multi_qudratic}
\end{figure}

 We write $\bx = (x_1, \ldots, x_d)^{\top}$.
 We define $\kappa : \NN \to 2\NN_0$ as 
 \[
\kappa(n) \coloneq   \begin{cases}
     n &n \text{ is even},\\
     n-1 &n \text{ is odd}.\\
 \end{cases}
 \]
 Consider arbitrary $p,q \in \NN$ with $pq \geq d$.
 By Theorem~\ref{thm:quadratic_approximation}, there exists a HyCNN $g \colon \RR\to \RR$ with $\lfloor L/p \rfloor$ hidden layers, $\kappa(\lfloor (m-1)/q \rfloor)$ neurons per layer and $\sigma(a,b) = \max(a,b)$, such that 
     \begin{align}
        \sup_{x\in [0,1]}|g(x) - x^2| \leq \frac{1}{8} \kappa\left(\left\lfloor \frac{m-1}{q} \right\rfloor\right)^{-2 \lfloor L/p \rfloor} \leq \frac{1}{8} \left\lfloor \frac{m-1}{q} -1 \right\rfloor^{-2 \lfloor L/p \rfloor}. 
        \label{eq.8gfew}
     \end{align}
     We construct a HyCNN $f\colon \RR^d \to \RR$ with $L$ hidden layers and $m$ neurons per layer as follows. 
    For each $j \in [p]$,
    we approximate $x_{(j-1)q+1}^2,\ldots, x_{j q}^2$ by applying $q$ parallel copies of the HyCNN $g$ in the hidden layers from $((j-1)\lfloor L/p \rfloor+1)$ to $j \lfloor L/p \rfloor$ of $f$. 
    This is possible as the network input is accessible in each hidden layer.
    If $pq > d$, we apply the construction only up to index $d$. 
    This construction requires $p \lfloor L/p \rfloor \leq L$ layers and $q \kappa(\lfloor (m-1)/q \rfloor) \leq m-1$ neurons per layer.

    It remains to sum the outputs $g(x_1), \ldots, g(x_d)$.
    This can be done by adding one neuron per hidden layer that stores the sum of the approximated square functions using 
    $$\max\big( g(x_1)+\ldots + g(x_k), -d \big) = g(x_1)+\ldots + g(x_k), \qquad \forall k \in [d].$$
    See Figure~\ref{fig_multi_qudratic} for an illustration.
    The HyCNN output $f(\bx)$ is then $\sum_{i=1}^d g(x_i)$. By triangle inequality and \eqref{eq.8gfew}, the approximation error is upper bounded by 
    \[
    \sup_{\bx\in [0,1]^d} \big|f(\bx) - \|\bx\|_2^2\big| \leq \sum_{i=1}^d \sup_{x_i \in [0,1]^d} \big|g(x_i) - x_i^2 \big| \leq \frac{d}{8} \inf_{p,q \in \NN: pq \geq d} \,  \left\lfloor \frac{m-1}{q}-1 \right\rfloor^{-2\lfloor L/p \rfloor}.
    \]   
\end{proof}

\subsection{Proof of Inclusions \eqref{eq.84gr}} \label{appendix_proof_equation_inclusion}
\begin{proof}
    We write $\bx = (x_1,\ldots,x_d)^{\top}$.
    Theorems \ref{thm:lowerBoundPiecewiseLinear} and \ref{thm:quadratic_approximation} yield
    \[
    \inf_{f \in \ICNN_d(L,m)} \,  \sup_{\bx \in [0,1]^d}|f(\bx)-x_1^2| \geq \frac{1}{8 (m + 2(L-1)m)^2} > \frac{1}{8(2mL)^2}
    \]
    and
    \[
    \inf_{h \in \HyCNN_d(L',m')} \sup_{\bx \in [0,1]^d}|f(\bx)-x_1^2| \leq \frac{1}{8 (m')^{L'}} \leq \frac{1}{8(2mL)^2}.
    \]
    respectively. Hence, we get $\HyCNN_d(L',m') \subsetneq \ICNN_d(L,m)$. 

    The second assertion follows by setting
    $V_\ell^{2} = W_\ell^{2} = 0$ and $\bb_\ell^{2} = 0$ for each $\ell = 0, \ldots, L-1$ in \eqref{eq:HyCNN}.
    %

    To establish the last inclusion, write $(x_1,\ldots, x_d)_+ \coloneqq (x_1 \vee 0, \ldots, x_d \vee 0)$.
    For a given HyCNN $h \in \HyCNN_d(L,m)$,
    we construct a ReLU network $f \in \ReLU_d(L,3m+2d)$ that represents $h$.
    In each hidden layer of $f$, we store $\bx_+$ and $(-\bx)_+$, which represent the positive and negative parts of input vector, respectively.
    This requires $2d$ neurons per layer, and these neurons can be used to represent skip connections from the input via 
    \[
        \ba^{\top} \bx = \ba^{\top}\big(\bx_+ - (-\bx)_+\big) = \ba^{\top} \bx_+ - \ba^{\top} (-\bx)_+.
    \]
    On the other hand, from 
    $x \vee y = x + (y-x)_+$ and $x = x_+ - (-x)_+$,
    we have
    \begin{align*}
            (\ba_1^{\top} \bz + b_1) 
    \vee (\ba_2^{\top} \bz + b_2) 
    &= (\ba_1^{\top} \bz + b_1) + \big( (\ba_2 - \ba_1)^{\top} \bz + b_2 - b_1 \big)_+\\  
    &= (\ba_1^{\top} \bz + b_1)_+ - (-\ba_1^{\top} \bz - b_1)_+  + \big( (\ba_2 - \ba_1)^{\top} \bz + b_2 - b_1 \big)_+.    
    \end{align*}
    Hence, instead of $m$ neurons in each hidden layer of $h$ computing the right hand side of the previous identity, $3m$ neurons in the ReLU network $f$ can compute the right hand side.
    This proves the assertion.
\end{proof}

\section{Derivation of the Initialization Scheme for HyCNNs} \label{appendix_init}
In this section, we derive the initialization scheme introduced in Section \ref{sec:HyCNNs}, closely following the steps for the ICNN initialization proposed by \cite{hoedt2023principled} but appropriately adapted for HyCNNs.

For $\ell \in [L-1]$, 
we rewrite the HyCNN layer \eqref{eq:HyCNN} as
\begin{align*}
    \bs_{\ell+1} &:= V_{\ell}^{1} \bz_{\ell} + W_{\ell}^{1} \bx + \bb_{\ell}^{1}, \\
    \bt_{\ell+1} &:= V_{\ell}^{2} \bz_{\ell} + W_{\ell}^{2} \bx + \bb_{\ell}^{2}, \\
    \bz_{\ell+1} &:= \max(\bs_{\ell+1}, \bt_{\ell+1}).
\end{align*}
We write $\bx = (x_i)_{i \in [d]}$ and for $k \in \{1,2\}$,
\begin{align*}
    \bs_{\ell} = (s_{\ell, i})_{i \in [d_{\ell}]}, \quad \bt_{\ell} &= (t_{\ell, i})_{i \in [d_{\ell}]}, \quad \bz_{\ell} = (z_{\ell, i})_{i \in [d_{\ell}]}, \quad \text{for all} \ \ell \in [L], \\
    \quad V_{\ell}^k = (v^{(k)}_{\ell,i,j})_{i \in [d_{\ell+1}], j \in [d_{\ell}]}, \quad
    W_{\ell}^k &= (w^{(k)}_{\ell,i,j})_{i \in [d_{\ell+1}], j \in [d]}, \quad \bb^k_{\ell} = (b^{(k)}_{\ell,i})_{i \in [d_{\ell+1}]} \quad \text{for all} \ \ell\in [L-1].
\end{align*}
%
%
%
At initialization, the weight parameters are drawn independently with distributions ($\ell \in [L-1]$),
\begin{align*}
    v_{\ell, i,j}^{(k)} &\sim \calD_{\ell}, && k \in \{1,2\}, \, i \in [d_{\ell+1}], \, j \in [d_{\ell}],\\
    w_{\ell, i,j}^{(k)} &\sim N(0, \sigma_{w, \ell}^2), && k \in \{1,2\}, \, i \in [d_{\ell+1}], \, j \in [d],\\
    b_{\ell, i}^{(k)} &\sim N(\mu_{b, \ell}, \sigma_{b, \ell}^2), && k \in \{1,2\}, \, i \in [d_{\ell+1}],    
\end{align*}
where $\calD_{\ell}$ is a distribution in a pre-specified class with support on $\RR_+$. 
Denote by $\mu_{v,\ell}$ and $\sigma_{v,\ell}^2$ the expectation and the variance of $\calD_{\ell}$, respectively.  
%
For each $\ell \in [L]$, the $2d_{\ell}$
random variables 
$s_{\ell,1}, t_{\ell,1}, \ldots, s_{\ell,d_\ell}, t_{\ell,d_\ell}$
are exchangeable.
It follows that $\EE(s_{\ell,1}) = \EE(s_{\ell,i}) = \EE(t_{\ell,i})$, $\EE(s_{\ell,1}^2) = \EE(s_{\ell,i}^2) = \EE(t_{\ell,i}^2)$ and 
$\EE(s_{\ell,1} t_{\ell,1}) =  \EE(s_{\ell,i} s_{\ell,i'}) = \EE(t_{\ell,i} t_{\ell,i'}) = 
\EE(s_{\ell,i} t_{\ell,i}) = \EE(s_{\ell,i} t_{\ell,i'})$ for any $i, i' \in [d_{\ell}]$ with $i \neq i'$.
Moreover,
$\EE(z_{\ell,1}) = \EE(z_{\ell,i})$, $\EE(z_{\ell,1}^2) = \EE(z_{\ell,i}^2),$ and $\EE(z_{\ell,1} z_{\ell,2}) = \EE(z_{\ell,i} z_{\ell,i'}).$

We now fix a layer $\ell \in [L-1]$.
By definition, for $i \in [d_{\ell+1}]$ we have 
\begin{align}
    s_{\ell+1,i} &= \sum_{j=1}^{d_{\ell}} v_{\ell, i, j}^{(1)} z_{\ell, j} + \sum_{j=1}^d w_{\ell, i, j}^{(1)} x_j + b_{\ell, i}^{(1)}, \label{tmp_20} \\
    t_{\ell+1,i} &= \sum_{j=1}^{d_{\ell}} v_{\ell, i, j}^{(2)} z_{\ell, j} + \sum_{j=1}^d w_{\ell, i, j}^{(2)} x_j + b_{\ell, i}^{(2)}
    \label{tmp_21}
\end{align} 
with
$$z_{\ell,j} = s_{\ell,j} \vee t_{\ell,j}.$$

The key objective is to ensure
that pre-activations exhibit comparable statistical properties across all layers at initialization.
To this end, we derive fixed-point equations for the mean, variance, and covariance, 
\begin{align}
    \EE(s_{\ell+1,1}) = \EE(s_{\ell,1}), \quad
    \EE(s^2_{\ell+1,1}) = \EE(s_{\ell,1}^2), \quad 
    \EE(s_{\ell+1,1} t_{\ell+1,1}) = \EE(s_{\ell,1} t_{\ell,1}),  \label{sp_cond}
\end{align} 
and identify suitable hyperparameter configurations
$(\mu_{v,\ell}, \sigma_{v,\ell}^2, \sigma_{w,\ell}^2, \mu_{b,\ell}, \sigma_{b,\ell}^2)$.
For simplicity, we drop the subscript $\ell$ from the hyperparameters below.  
From \eqref{tmp_20} and \eqref{tmp_21}, 
\begin{align*}
    &\EE(s_{\ell+1,1}) = d_{\ell} \mu_v \EE(z_{\ell,1}) + \mu_b,\\
    &\EE(s^2_{\ell+1,1}) = \sigma_b^2 + \mu_b^2 + \sigma_w^2 \|\bx\|_2^2 + d_{\ell}(\mu_v^2 + \sigma_v^2) \EE(z_{\ell,1}^2) + d_{\ell}(d_{\ell}-1) \mu_v^2 \EE(z_{\ell,1} z_{\ell,2}) + 2d_{\ell} \mu_b \mu_v \EE(z_{\ell,1}),\\
    &\EE(s_{\ell+1,1} t_{\ell+1,1}) = \mu_b^2 + d_{\ell} \mu_v^2 \EE(z_{\ell,1}^2) + d_{\ell}(d_{\ell}-1) \mu_v^2 \EE(z_{\ell,1} z_{\ell,2}) + 2d_{\ell} \mu_b \mu_v \EE(z_{\ell,1}).
\end{align*}
Assume we already picked hyperparameters in the previous layer so that $\EE(s_{\ell,1}) =0$. 
Choosing $\mu_b = -d_{\ell} \mu_v \EE(z_{\ell,1})$ ensures then $\EE(s_{\ell+1,1}) = 0,$
$\mu_b^2 + 2d_{\ell} \mu_v \mu_b \EE(z_{\ell,1}) = -d_{\ell}^2 \mu_v^2 \EE(z_{\ell,1})^2$, and
\begin{align}
    %
    &\EE(s^2_{\ell+1,1}) = \sigma_b^2 + \sigma_w^2 \|\bx\|_2^2 + d_{\ell}(\mu_v^2 + \sigma_v^2) \EE(z_{\ell,1}^2)  + d_{\ell}(d_{\ell}-1) \mu_v^2 \EE(z_{\ell,1} z_{\ell,2}) -d_{\ell}^2 \mu_v^2 \EE(z_{\ell,1})^2, \label{eq_sm_1}\\
    &\EE(s_{\ell+1,1} t_{\ell+1,1}) =  d_{\ell} \mu_v^2 \EE(z_{\ell,1}^2)  + d_{\ell}(d_{\ell}-1) \mu_v^2 \EE(z_{\ell,1} z_{\ell,2}) -d_{\ell}^2 \mu_v^2 \EE(z_{\ell,1})^2.\label{eq_sm_2}
\end{align}
The joint distribution of the random variables $s_{\ell,1},\ldots,s_{\ell,d_{\ell}},t_{\ell,1},\ldots,t_{\ell,d_{\ell}}$ by a Gaussian distribution with the same mean and covariance matrix. Define $A := \EE(s_{\ell,1}^2)$ and $B := \EE(s_{\ell,1} t_{\ell,1})$. Applying Lemma \ref{lemma_mul_momentum} with $(X,Y,Z,W)=(s_{\ell,1}, t_{\ell,1}, s_{\ell,2}, t_{\ell,2})$, $\sigma^2=A$, and $\rho=B/A,$ we have
\begin{align}
    \EE(z_{\ell,1}) &= \EE(s_{\ell,1} \vee t_{\ell,1}) = \sqrt{\frac{A-B}{\pi}}, \label{eq_zm_1}
    \\
    \EE(z_{\ell,1}^2) &= \EE\big((s_{\ell,1} \vee t_{\ell,1})^2\big) = A, \label{eq_zm_2} 
    \\
    \EE(z_{\ell,1} z_{\ell,2}) &= \EE\big((s_{\ell,1} \vee t_{\ell,1}) (s_{\ell,2} \vee t_{\ell,2})\big) = B + \frac{A-B}{\pi}. \label{eq_zm_3} 
\end{align}
Now, we
solve the equations \eqref{sp_cond}.
By plugging \eqref{eq_zm_1}, \eqref{eq_zm_2} and \eqref{eq_zm_3} into \eqref{eq_sm_1}, we obtain
\begin{align}
    A = \EE(s_{\ell+1,1}^2) 
    %
    &= \sigma_b^2 + \sigma_w^2 \|\bx\|_2^2 + d_{\ell}(\mu_v^2 + \sigma_v^2) A + d_{\ell}(d_{\ell}-1) \mu_v^2 \left(B + \frac{A-B}{\pi} \right) - d_{\ell}^2 \mu_v^2 \frac{A-B}{\pi} \nonumber\\
    &= \sigma_b^2 + \sigma_w^2 \|\bx\|_2^2 + d_{\ell}(\mu_v^2 + \sigma_v^2) A + d_{\ell}(d_{\ell}-1) \mu_v^2 B -d_{\ell} \mu_v^2 \frac{A-B}{\pi}.
    \label{tmp_2}
\end{align}
Similarly, by plugging \eqref{eq_zm_1}, \eqref{eq_zm_2} and \eqref{eq_zm_3} into \eqref{eq_sm_2}, we obtain
\begin{align}
    B = \EE(s_{\ell+1, 1} t_{\ell+1, 1}) 
    %
    &= d_{\ell} \mu_v^2 A + d_{\ell}(d_{\ell}-1) \mu_v^2 B -d_{\ell} \mu_v^2 \frac{A-B}{\pi}.
    \label{tmp_3}
\end{align}
Using $\rho = B/A,$ \eqref{tmp_3} yields
$$\mu_v^2 = \frac{B}{d_{\ell}A + d_{\ell}(d_{\ell}-1)B - \tfrac{d_{\ell}(A-B)}{\pi}} = \frac{\rho}{d_{\ell} + d_{\ell}(d_{\ell}-1)\rho - \tfrac{d_{\ell}(1-\rho)}{\pi}}.$$
Also, by subtracting \eqref{tmp_3} from \eqref{tmp_2} we get
$$A(1 - \rho) = \sigma_b^2 + \sigma_w^2 \|\bx\|_2^2 + d_{\ell}\sigma_v^2 A.$$
Since the extreme cases $\rho = 0 = \mu_v^2$ and $\rho = 1$ are undesirable, we choose $\rho = \tfrac12$.
It follows
$$\mu_v = \sqrt{\frac{1}{d_{\ell}^2 + (1-\tfrac{1}{\pi})d_{\ell}}}$$
and
$$\frac{1}{2}A = \sigma_b^2 + \sigma_w^2 \|\bx\|_2^2 + d_{\ell}\sigma_v^2 A.$$
Provided that $\|\bx\|_2^2 \approx d$, a reasonable choice for other hyperparameters would be $\sigma_b^2 = 0$, $\sigma_w^2 = 1/(4d)$ and $\sigma_v^2 = 1/(4d_{\ell})$.
Then we get $A = 1$ and $B=\tfrac12$.
Finally, we obtain
$$\mu_b = -d_{\ell} \mu_v \EE(z_{\ell, 1}) = -d_{\ell}  \sqrt{\frac{1}{d_{\ell}^2 + (1-\tfrac{1}{\pi})d_{\ell}}}
\sqrt{\frac{1}{2 \pi}} =  -  \sqrt{\frac{d_{\ell}}{2 \pi d_{\ell} + 2 \pi -2}}.$$

\begin{lemma} \label{lemma_mul_momentum}
If $\rho \in (-1,1)$ and
    $$
\begin{pmatrix}
X \\ Y \\ Z \\ W
\end{pmatrix}
\sim \mathcal{N}\!\left(
\begin{pmatrix}
0 \\ 0 \\ 0 \\ 0
\end{pmatrix},
\,
\sigma^2
\begin{pmatrix}
1      & \rho & \rho & \rho \\
\rho   & 1    & \rho & \rho \\
\rho   & \rho & 1    & \rho \\
\rho   & \rho & \rho & 1
\end{pmatrix}
\right),
$$
then, 
\begin{align*}
    \EE[X \vee Y] =  \sigma \sqrt{\frac{1-\rho}{\pi}}, \quad
\EE[(X \vee Y)^2] = \sigma^2, \quad
\EE[(X \vee Y)(Z \vee W)] = \left(\rho + \frac{1-\rho}{\pi} \right) \sigma^2.
\end{align*}
\end{lemma}
\begin{proof}
    We define 
    $$S_1 := X+Y, \quad S_2 := Z+W, \quad D_1 := X-Y, \quad D_2 := Z-W.$$
    Since $(S_1, S_2, D_1, D_2)^{\top}$ is jointly Gaussian and $\operatorname{Var}(X)=\operatorname{Var}(Y)=\operatorname{Var}(Z)=\operatorname{Var}(W)=1$, we have $S_1 \perp D_1, S_1 \perp D_2, S_2 \perp D_1, S_2 \perp D_2$, $D_1 \perp D_2$ and
    $$X \vee Y = \frac{S_1 + |D_1|}{2}, \quad Z \vee W = \frac{S_2 + |D_2|}{2}.$$
    The absolute value of a standard Gaussian random variable has mean $\sqrt{2/\pi}$.
    From $S_1, S_2 \sim N(0, 2\sigma^2(1+\rho))$ and $D_1, D_2 \sim N(0, 2\sigma^2(1-\rho))$, we get
    \begin{align*}
        \EE[X \vee Y] = \EE\left[\frac{S_1 + |D_1|}{2}\right] = \frac{1}{2}\sqrt{\frac{4\sigma^2(1-\rho)}{\pi}} = \sigma \sqrt{\frac{1-\rho}{\pi}}
    \end{align*}
    and
    \begin{align*}
        \EE\big((X \vee Y)^2\big) 
        = \EE\left(\frac{S_1^2 + D_1^2 + 2S_1 |D_1|}{4}\right)
        = \frac{2\sigma^2(1+\rho) + 2\sigma^2(1-\rho)}{4} = \sigma^2.
    \end{align*}    
    We derive the last statement from
    \begin{align*}
        \EE\big((X \vee Y)(Z \vee W)\big) &= \EE\left(\frac{S_1 S_2 + S_1 |D_2| + S_2 |D_1| + |D_1||D_2|}{4}\right)\\
        &= \EE\left(\frac{(X+Y)(Z+W)}{4}\right) + \frac{1}{4}\EE(|D_1|)(|D_2|)\\
        &= \rho \sigma^2 + \frac{1-\rho}{\pi}\sigma^2.
    \end{align*}
\end{proof}

 

%

%
%
%

%
%
%

%
%

%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%

\renewcommand{\parabold}[1]{\paragraph{#1.}}
\section{Additional Experiments}\label{app:additional_experiments}

In this section, we provide additional experimental results and implementation details complementing the experiments described in \Cref{sec:experiments}. The section is organized as follows. In \Cref{app:initialization_visualization}, we visualize randomly initialized HyCNNs. In \Cref{app:regression_experiments}, we present additional regression experiments, including algorithmic details, univariate regression fits, results across different sample sizes and dimensions, and detailed performance tables. In \Cref{app:OT_experiments}, we present the HyCNN-based OT map estimation procedure, simulation settings, and detailed performance tables. 
All experiments were run on a MacBook Pro 16" with Apple M4 Pro with 24\,GB of unified memory and 512GB of storage using the integrated GPU with the Metal framework. ChatGPT~5.4 Codex and Claude Code Opus~4.6 were used to assist in implementation and debugging, and generated code was carefully reviewed and tested by the authors. The code to some experiments is provided on GitHub at \url{https://www.github.com/hundrieser/HyCNN}.

Beyond the experiments reported in the paper, the full research project required additional compute for preliminary and exploratory work that is not included in the final manuscript. This includes the development and validation of the HyCNN initialization scheme, hyperparameter exploration (e.g., learning rate, batch size, number of epochs, width, and depth), ablations on skip-connection variants, as well as failed runs and debugging. All such runs were executed on the same hardware described above. We estimate that the total compute consumed during the project exceeded that required to reproduce the reported experiments by approximately a factor of three to five. %

\subsection{Visualization of HyCNN initialization}\label{app:initialization_visualization}

Following our initialization scheme from \Cref{sec:HyCNNs}, we display the surfaces of randomly initialized HyCNNs across different depths in \Cref{fig:HyCNN_init_vis} for input dimension $d=2$ (i.e. $\bx\in [-10,10]^2$) and width $m = 32$. Upon close inspection, we see that shallow networks behave more polyhedral, while deeper networks exhibit more smoothness. Moreover, the surfaces also do not explode at initialization as the depth increases, and are roughly centered around the origin.

\begin{figure}[h!]
    \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim=0 0 0 0, clip]{../figures/hycnn_init_vis_sd.png}}%
        \caption{HyCNNs at initialization across different depths. Each panel shows a single randomly initialized HyCNN according to the initialization scheme from \Cref{sec:trainingHyCNNs} with maxout activation, input dimension $d=2$, domain $\bx\in [-10,10]^2$, width $m = 32$, and depths $L\in \{2,4,6,8\}$. The surface plot is shown together with its contour projection on the base plane. The visualization demonstrates that the initialized functions remain bounded and roughly centered around the origin as depth increases, and that deeper networks produce smoother surfaces compared to the more polyhedral shallow networks.}
         \label{fig:HyCNN_init_vis}
         \end{center}
\end{figure}

\subsection{Regression experiments}\label{app:regression_experiments}

In this section, we provide details and additional simulations to the regression experiments described in \Cref{sec:experiments}. We first describe the experimental setup, then present univariate regression fits (\Cref{app:univariate_regression}), $50$-dimensional regression across different sample sizes (\Cref{app:regression_dim50}), regression across different dimensions (\Cref{app:regression_dimensions}), and interpolation across different dimensions (\Cref{app:interpolation}).

In total, we consider the following ground-truth functions:
\begin{align*}
&\textstyle \text{(a) } f_1(\bx) = \|\bx\|^2_2, &&\text{(b) } f_2(\bx) = \|\bx\|_4^4, \;&&\text{(c) } f_3(\bx) = \|\bx\|^2_2 + 0.25\sin\left(20\|\bx\|_2\right),\\
       &\textstyle\text{(d) } f_4(\bx) = \|\bx\|_1, &&\textstyle \text{(e) } f_5(\bx) = \exp(\|\bx\|_1/\sqrt{d}),&&\textstyle \text{(f) } f_6(\bx) =\max\left(\|\bx-\boldsymbol{\mu}\|_2^2, \|\bx+\boldsymbol{\mu}\|_2^2\right),
\end{align*}
where for every generated sample, we first draw the entries of the vector $\boldsymbol{\mu} \in \RR^d$ independently from $N(0,1/d)$.  %

\parabold{Data generation}
We draw training samples $(\bx_i, f(\bx_i) + \epsilon_i)_{i=1}^n$ with $\bx_i$ drawn independently from $\text{Unif}([-1,1]^d)$ and the noise $\epsilon_i$ drawn independently from $N(0,\sigma^2)$ for $\sigma^2 \geq 0$.

\parabold{Network architectures}
We compare MLPs with ReLU activation, ICNNs with ReLU activation, GroupMax networks (i.e., HyCNNs without skip connections) and HyCNNs. For each architecture, we consider networks of depth $L = 2,4,8, 16, 32$ and width $m =64$ for MLP and ICNN, and width $m = 48$ for GroupMax and HyCNN. %

\parabold{Training}
For each architecture $\hat f_\theta$ we first normalize the data per
coordinate by subtracting the empirical mean and dividing by the empirical standard deviation along each input dimension. Each network is then trained on the standardised data, and finally the trained models are destandardized to compute the reported MSE in the original units. For training, we perform empirical risk minimization with respect to the mean-squared-error loss, i.e., we minimize
\begin{align*}
\theta \;\mapsto\; \frac{1}{n}\sum_{i=1}^{n}\big(\hat f_\theta(\bx_i) - y_i\big)^2,
\end{align*}
over the full training set $(\bx_i, y_i)_{i=1}^n$, where $y_i = f(\bx_i) + \epsilon_i$. Optimization is carried out with the Adam optimizer \citep{kingma2014adam} with learning rate $\lambda = 10^{-2}$, $\beta_1 = 0.9$, $\beta_2 = 0.999$, batch size $\min(n, 1000)$, and $100$ epochs, applied jointly to all trainable parameters. For the ICNN and HyCNN architectures, the hidden-to-hidden weight matrices $V_\ell$ must remain elementwise non-negative throughout training, as this is required for the resulting network to be input-convex in $\bx$. We impose this constraint via a smooth reparametrization of the weights: we store an unconstrained parameter tensor $R_\ell \in \RR^{n_{\ell+1}\times n_\ell}$ and use, on every forward pass, the effective weight $V_\ell = \operatorname{softplus}(R_\ell) = \log(1 + \exp(R_\ell))$, applied entrywise. Because $\operatorname{softplus}\colon \RR \to (0,\infty)$ is smooth and strictly positive, the entries of $V_\ell$ are automatically non-negative for every value of $R_\ell$, and gradients flow back through the softplus so that Adam can be applied to the unconstrained $R_\ell$ directly. All other parameters (input-to-hidden weights, biases, quadratic-skip matrices where applicable) are unconstrained real-valued parameters and are updated without any reparametrization.

For initialization, we use for the HyCNNs the scheme described in \Cref{sec:HyCNNs} (the initialiaztion acts directly on $V_\ell$ and not on $R_{\ell}$),  for the ICNN we use the initialization scheme of \citet{hoedt2023principled}, for GroupMax networks we use the same initialization scheme as for HyCNNs while setting the skip connection weights to zero, and for MLPs we use PyTorch's default initialization scheme for \texttt{nn.Linear} layers, which draws each weight entry independently from $\mathrm{Uniform}(-1/\sqrt{d_{\mathrm{in}}},\, 1/\sqrt{d_{\mathrm{in}}})$, where $d_{\mathrm{in}}$ denotes the number of input features to the respective layer; the bias vector is sampled from the same distribution. Internally, PyTorch implements this via \texttt{kaiming\_uniform\_(a=math.sqrt(5))} \citep{he2015delving}, which with $a=\sqrt{5}$ reduces the Kaiming bound $\sqrt{6/((1+a^2)\cdot d_{\mathrm{in}})}$ to $1/\sqrt{d_{\mathrm{in}}}$.

\parabold{Evaluation}
Given a trained network $\hat f$, we evaluate the prediction MSE on an independent test set $(\tilde \bx_j)_{j=1}^{N_{\mathrm{test}}}$ of size $N_{\mathrm{test}} = 1000$ drawn from $\textup{Unif}([-1,1]^d)$ (i.e., the same distribution as the training covariates but without noise), defined as
\begin{equation}\label{eq:prediction_MSE}
    \mathrm{MSE}_{\mathrm{pred}} \coloneqq \frac{1}{N_{\mathrm{test}}} \sum_{j=1}^{N_{\mathrm{test}}} \big( f(\tilde \bx_j) - \hat f(\tilde \bx_j) \big)^2,
\end{equation}
where $f$ denotes the ground-truth function. Each simulation run, except for the univariate regression which is only conducted once for visualization, is repeated $10$ times with different random seeds for the training sample generation and the network initialization.

\subsubsection{Univariate regression}\label{app:univariate_regression}

For univariate regression $(d = 1)$, we visualize the fits of the different architectures across different depths for the ground-truth functions (a--f) and different noise levels. \Cref{fig:Univariate_regression} shows the best MLP, ICNN and GroupMax network across the different depths, and the outcome of different HyCNNs architectures. We see that deeper HyCNNs often exhibit a better fit than more shallow HyCNNs. Except for the function $f_3$ which is non-convex, the best MLP, ICNN and GroupMax network across the different depths often exhibit a worse fit than the best HyCNN across the different depths. Moreover, for the non-convex function $f_3$, the best convex shape-constrained network is given by a HyCNN.

\begin{figure}[h!]
    \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim=0 0 0 0, clip]{../figures/FIG_5_UniVariate_multitask.pdf}}%
        \caption{Univariate regression results ($d = 1$) for the six ground-truth functions (a--f) from \Cref{app:regression_experiments}. Each panel shows the fitted curves of HyCNNs (width $48$) with depths $L \in \{2,4,8,16,32\}$ and the best MLP (width $64$), ICNN (width $64$), or GMN (width $48$) among the same depths; the green dots depict the training samples and the black curve depicts the ground-truth function. For each function, the visualization is based on a single run (no averaging over seeds) with $n = 5{,}000$ training samples. Noise levels: $\sigma = 1$ for $f_1, f_2, f_5, f_6$ and $\sigma = 0$ for $f_3, f_4$. The best MLP, ICNN, and GMN are selected as the architecture with the lowest prediction MSE among all depths.}
         \label{fig:Univariate_regression}
         \end{center}
\end{figure}

\subsubsection{Regression in dimension $d = 50$ across different sample sizes}\label{app:regression_dim50}

We consider regression in dimension $50$ across different sample sizes $n \in \{100, 500, 1000, 5000, $ $10000\}$ and visualize the prediction MSE in Figures \ref{fig:HyCNN_training_dim50} and \ref{fig:HyCNN_training_dim50_part2} for the same collection of functions (a--f) as before. We see that deeper HyCNNs often exhibit a better fit than more shallow HyCNNs across different sample sizes. Moreover, the best MLP, ICNN and GroupMax network across the different depths often exhibit a worse fit than the best HyCNN across the different depths, especially for larger sample sizes. In particular, even for the non-convex function $f_3$, the best network is nonetheless a HyCNN, which is likely due to the fact that $f_3$ is well approximated by a convex function. For sample sizes several orders of magnitude larger, it is likely that the MLP will perform best, however for the sample sizes considered here, it seems that the HyCNNs are able to more effectively leverage the inductive bias of convexity to achieve better generalization performance than the MLPs.

\begin{figure}[t!]
%
  \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim = 0 0 0 0, clip]{../figures/FIG_4_MSE_vs_NTrain_multitask_best_at_n10000_part2.pdf}}
    %
    \caption{Prediction MSE for different training sample sizes $n$ for the $50$-dimensional regression tasks with 10th-90th percentile bands across $10$ runs. Each panel shows HyCNNs with depths $2,4,8,16$ and the best MLP, ICNN, GMN at $n = 10^4$ among similar depths. %
    }
    \label{fig:HyCNN_training_dim50_part2}
  \end{center}
\end{figure}

\subsubsection{Regression across different dimensions for sample size $n = 5000$}\label{app:regression_dimensions}

We display the prediction MSE for the same collection of functions (a--f) across different dimensions $d \in \{1,2,5,10,20,50\}$ for a fixed sample size of $n = 5000$ in the noisy setting with additive Gaussian noise ($\sigma = 1$ for $f_1, f_2,  f_4, f_5, f_6$ and $\sigma = 0$ for $f_3$). The results are reported in \Cref{tab:model_l2} ($f_1$), \Cref{tab:model_l4} ($f_2$), \Cref{tab:model_quadratic_sinusoidal} ($f_3$), \Cref{tab:model_l1} ($f_4$), \Cref{tab:model_piecewise_quadratic} ($f_5$), and \Cref{tab:model_exp} ($f_6$).

Across all settings, the key observations are consistent: HyCNNs with depth at least four consistently achieve the lowest prediction MSE, particularly in higher dimensions ($d \geq 10$), and in most examples also consistently outperform both ICNNs and MLPs. GroupMax networks are occasionally competitive with HyCNNs at moderate depths, which may be attributed to their smaller model size providing implicit regularization. Deeper HyCNNs tend to improve performance as the dimension increases, with depth $L = 16$ often providing the best results for $d = 50$. Very deep architectures ($L = 32$) can exhibit instabilities due to occasional training failures, as reflected in the larger standard errors. In contrast, ICNNs and GMNs degrade substantially beyond depth $8$: ICNNs at depth $32$ often exhibit numerical instabilities (MSE $> 10^{11}$), and GMNs at depth $32$ consistently diverge. Since GroupMax networks are HyCNNs without skip connections from the input, this suggests that the skip connections play a critical role in stabilizing training of deeper architectures. MLPs, while trainable at all depths, underperform the convex architectures for most functions and dimensions, reflecting their lack of inductive bias towards convexity.
For the non-convex function $f_3$, the picture is more nuanced: in low dimensions ($d \leq 5$), the MLP performs considerably better than the convex architectures, as it is not constrained to produce convex fits. However, for $d \geq 10$ the HyCNN achieves the best prediction MSE, suggesting that the convexity bias of HyCNNs acts as a beneficial regularizer in higher dimensions, where $f_3$ is well approximated by a convex function.

\begin{table}[h!]
\caption{Prediction MSE and standard error (SE) by network and dimension (\textbf{all entries multiplied by $10^2$}; rounded to 2 decimal places) for learning the function $f(\bx) = \|\bx\|^2$ based on $n = 5,000$ data points $\bX_i \sim \text{Unif}([-1,1]^d)$ and $Y_i = f_1(\bX_i) + \epsilon_i$ with $\epsilon_i \sim N(0, 1)$. Three network types are considered: MLP, ICNN and HyCNN, and for each network type, five architectures with different depths are considered. The networks are trained for 100 epochs, mean and SE are computed over $10$ different seeds, see the main text for more details. For each dimension $d$, the smallest prediction MSE per network type is bold and colored. The \underline{three smallest mean prediction errors} across all networks are underlined. }
\label{tab:model_l2}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & \textcolor[HTML]{f85d42}{\textbf{0.24}} (0.04) & \textcolor[HTML]{f85d42}{\textbf{1.00}} (0.09) & \textcolor[HTML]{f85d42}{\textbf{8.17}} (0.43) & \textcolor[HTML]{f85d42}{\textbf{29.47}} (0.82) & \textcolor[HTML]{f85d42}{\textbf{80.39}} (2.04) & 534.74 (22.01) \\
 & $(64\times 4)$ & 0.29 (0.05) & 1.66 (0.17) & 27.54 (1.76) & 72.65 (1.96) & 114.46 (5.00) & 476.37 (10.57) \\
 & $(64\times 8)$ & 0.46 (0.06) & 1.44 (0.09) & 22.76 (1.17) & 61.04 (2.94) & 92.29 (3.95) & 446.64 (14.96) \\
 & $(64\times 16)$ & 1.07 (0.53) & 4.80 (2.06) & 27.72 (4.91) & 53.84 (7.80) & 129.69 (17.93) & \textcolor[HTML]{f85d42}{\textbf{405.75}} (21.13) \\
 & $(64\times 32)$ & 8.89 (0.07) & 17.72 (0.23) & 44.41 (0.41) & 88.13 (1.18) & 174.51 (1.96) & 440.28 (3.97) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.16}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{0.41}} (0.03) & \textcolor[HTML]{F3A11C}{\textbf{2.31}} (0.07) & \textcolor[HTML]{F3A11C}{\textbf{8.59}} (0.33) & 32.08 (0.89) & 223.60 (4.45) \\
 & $(64\times 4)$ & 1.90 (1.09) & 3.81 (2.14) & 3.40 (0.93) & 16.58 (7.97) & \textcolor[HTML]{F3A11C}{\textbf{29.70}} (0.96) & \textcolor[HTML]{F3A11C}{\textbf{190.39}} (27.29) \\
 & $(64\times 8)$ & 8.90 (0.06) & 16.18 (1.64) & 40.19 (4.00) & 88.49 (1.28) & 135.80 (18.08) & 402.15 (29.32) \\
 & $(64\times 16)$ & 8.97 (0.07) & 17.78 (0.24) & 44.52 (0.39) & 88.43 (1.26) & 175.74 (2.09) & 445.51 (3.82) \\
 & $(64\times 32)$ & 8.90 (0.06) & 17.75 (0.24) & 44.52 (0.40) & 88.45 (1.27) & 175.75 (2.10) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & 0.14 (0.03) & 0.45 (0.03) & 2.23 (0.10) & 7.59 (0.20) & 29.23 (0.67) & 239.81 (3.59) \\
 & $(48\times 4)$ & \textcolor[HTML]{b842f8}{\underline{\textbf{0.11}}} (0.03) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.36}}} (0.02) & \textcolor[HTML]{b842f8}{\underline{\textbf{1.99}}} (0.05) & \textcolor[HTML]{b842f8}{\textbf{7.50}} (0.31) & \textcolor[HTML]{b842f8}{\textbf{28.58}} (0.58) & \textcolor[HTML]{b842f8}{\textbf{205.36}} (3.72) \\
 & $(48\times 8)$ & \underline{0.12} (0.03) & 0.42 (0.03) & 2.61 (0.33) & 8.40 (0.34) & 39.91 (4.20) & 241.19 (9.58) \\
 & $(48\times 16)$ & 1.20 (0.35) & 4.87 (0.70) & 15.09 (0.77) & 37.60 (1.03) & 92.25 (1.03) & 332.76 (4.39) \\
 & $(48\times 32)$ & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{5}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & 0.18 (0.03) & 0.57 (0.05) & 2.44 (0.08) & 7.62 (0.28) & 25.24 (0.60) & 167.86 (2.05) \\
 & $(48\times 4)$ & 0.14 (0.03) & 0.40 (0.03) & 2.01 (0.07) & \textcolor[HTML]{0080DB}{\underline{\textbf{6.61}}} (0.26) & \underline{21.27} (0.48) & \underline{122.17} (1.67) \\
 & $(48\times 8)$ & \textcolor[HTML]{0080DB}{\underline{\textbf{0.11}}} (0.03) & \underline{0.37} (0.03) & \underline{1.96} (0.07) & \underline{6.65} (0.33) & \textcolor[HTML]{0080DB}{\underline{\textbf{20.21}}} (0.39) & \underline{89.61} (1.83) \\
 & $(48\times 16)$ & 0.12 (0.04) & 0.38 (0.03) & \textcolor[HTML]{0080DB}{\underline{\textbf{1.89}}} (0.06) & \underline{7.18} (0.37) & \underline{21.05} (0.41) & \textcolor[HTML]{0080DB}{\underline{\textbf{67.56}}} (1.78) \\
 & $(48\times 32)$ & 0.14 (0.03) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.30}}} (0.03) & 2.97 (1.43) & 9.02 (1.63) & 38.40 (18.98) & 156.83 (53.48) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\begin{table}[h!]
\caption{Prediction MSE (standard error) for different models and dimensions (\textbf{all entries multiplied by $10^2$}), as in Table \ref{tab:model_l2}, but with true function $f_2(\bx) = \|\bx\|_4^4$. }
\label{tab:model_l4}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & \textcolor[HTML]{f85d42}{\textbf{0.26}} (0.04) & \textcolor[HTML]{f85d42}{\textbf{0.97}} (0.07) & \textcolor[HTML]{f85d42}{\textbf{11.25}} (0.39) & \textcolor[HTML]{f85d42}{\textbf{38.94}} (1.06) & \textcolor[HTML]{f85d42}{\textbf{100.21}} (2.99) & 507.67 (18.39) \\
 & $(64\times 4)$ & 0.33 (0.06) & 1.78 (0.14) & 30.17 (1.80) & 80.80 (2.22) & 131.05 (3.62) & 467.75 (9.59) \\
 & $(64\times 8)$ & 0.42 (0.06) & 1.26 (0.09) & 26.35 (1.33) & 71.66 (4.67) & 123.90 (4.56) & 421.46 (11.76) \\
 & $(64\times 16)$ & 1.27 (0.64) & 5.21 (1.90) & 20.05 (3.95) & 48.18 (5.59) & 115.96 (10.32) & 364.76 (14.61) \\
 & $(64\times 32)$ & 7.16 (0.08) & 14.36 (0.25) & 35.79 (0.41) & 70.67 (0.92) & 140.48 (1.96) & \textcolor[HTML]{f85d42}{\textbf{351.78}} (3.28) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.19}} (0.04) & \textcolor[HTML]{F3A11C}{\underline{\textbf{0.54}}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{4.29}} (0.08) & \textcolor[HTML]{F3A11C}{\textbf{13.47}} (0.37) & \textcolor[HTML]{F3A11C}{\textbf{39.75}} (1.00) & 227.44 (3.92) \\
 & $(64\times 4)$ & 1.71 (0.85) & 3.28 (1.72) & 7.69 (3.12) & 19.61 (5.91) & 40.47 (1.54) & \textcolor[HTML]{F3A11C}{\textbf{191.78}} (17.83) \\
 & $(64\times 8)$ & 7.17 (0.08) & 13.21 (1.29) & 32.71 (3.02) & 71.09 (1.00) & 115.52 (12.01) & 330.02 (17.17) \\
 & $(64\times 16)$ & 7.23 (0.09) & 14.41 (0.26) & 35.94 (0.40) & 71.04 (0.98) & 141.49 (2.04) & 355.71 (3.44) \\
 & $(64\times 32)$ & 7.17 (0.08) & 14.38 (0.25) & 35.94 (0.39) & 71.04 (0.99) & 141.51 (2.04) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & 0.30 (0.06) & 0.72 (0.07) & 4.68 (0.14) & 13.63 (0.29) & \textcolor[HTML]{b842f8}{\textbf{37.48}} (0.57) & 233.20 (3.87) \\
 & $(48\times 4)$ & 0.20 (0.04) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.54}}} (0.04) & \textcolor[HTML]{b842f8}{\textbf{4.20}} (0.07) & \textcolor[HTML]{b842f8}{\textbf{12.58}} (0.35) & 38.93 (0.45) & \textcolor[HTML]{b842f8}{\textbf{214.87}} (3.54) \\
 & $(48\times 8)$ & \textcolor[HTML]{b842f8}{\underline{\textbf{0.18}}} (0.03) & 0.63 (0.05) & 4.98 (0.23) & 14.17 (0.47) & 48.43 (3.08) & 230.92 (7.00) \\
 & $(48\times 16)$ & 1.88 (0.47) & 5.36 (0.73) & 13.68 (0.74) & 32.96 (0.69) & 81.86 (1.45) & 283.81 (6.02) \\
 & $(48\times 32)$ & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{5}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & 0.31 (0.04) & 1.08 (0.13) & 5.65 (0.10) & 13.25 (0.31) & \underline{34.56} (0.46) & 181.32 (3.52) \\
 & $(48\times 4)$ & 0.24 (0.03) & 0.68 (0.06) & \underline{4.10} (0.06) & \textcolor[HTML]{0080DB}{\underline{\textbf{12.07}}} (0.49) & \textcolor[HTML]{0080DB}{\underline{\textbf{32.07}}} (0.67) & \underline{141.57} (2.17) \\
 & $(48\times 8)$ & 0.21 (0.04) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.57}}} (0.04) & \underline{4.02} (0.07) & \underline{12.14} (0.47) & \underline{32.32} (0.47) & \underline{111.93} (2.13) \\
 & $(48\times 16)$ & \underline{0.19} (0.05) & 0.63 (0.04) & \textcolor[HTML]{0080DB}{\underline{\textbf{3.99}}} (0.05) & \underline{12.50} (0.45) & 35.59 (0.76) & \textcolor[HTML]{0080DB}{\underline{\textbf{95.91}}} (1.51) \\
 & $(48\times 32)$ & \textcolor[HTML]{0080DB}{\underline{\textbf{0.15}}} (0.03) & 0.65 (0.05) & 5.15 (1.36) & 14.64 (1.69) & 49.86 (18.36) & 172.35 (47.44) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\begin{table}[h!]
\caption{Prediction MSE (standard error) for different models and dimensions (\textbf{all entries multiplied by $10^2$}),  as in Table \ref{tab:model_l2}, but with true function $f_3(\bx) = \|\bx\|^2_2 + 0.25\sin(20\|\bx\|_2)$ and $\sigma = 0$. }
\label{tab:model_quadratic_sinusoidal}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & \underline{0.47} (0.08) & \underline{2.75} (0.05) & 3.58 (0.08) & 6.65 (0.13) & 28.30 (0.74) & 402.54 (17.86) \\
 & $(64\times 4)$ & \textcolor[HTML]{f85d42}{\underline{\textbf{0.09}}} (0.01) & \textcolor[HTML]{f85d42}{\underline{\textbf{0.46}}} (0.13) & \underline{2.02} (0.17) & 6.75 (0.25) & 28.84 (0.96) & 365.77 (10.40) \\
 & $(64\times 8)$ & \underline{0.23} (0.08) & \underline{0.48} (0.09) & \textcolor[HTML]{f85d42}{\underline{\textbf{1.20}}} (0.22) & \textcolor[HTML]{f85d42}{\textbf{5.19}} (0.32) & \textcolor[HTML]{f85d42}{\textbf{26.41}} (0.49) & \textcolor[HTML]{f85d42}{\textbf{309.46}} (13.46) \\
 & $(64\times 16)$ & 1.21 (0.20) & 4.96 (2.44) & 19.85 (7.01) & 31.01 (12.43) & 108.51 (23.51) & 326.82 (26.60) \\
 & $(64\times 32)$ & 10.89 (0.11) & 21.42 (0.31) & 47.31 (0.51) & 90.60 (1.13) & 177.66 (2.07) & 442.88 (3.95) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{2.74}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{3.05}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{3.59}} (0.05) & \textcolor[HTML]{F3A11C}{\textbf{6.04}} (0.07) & 21.53 (0.48) & 184.15 (3.06) \\
 & $(64\times 4)$ & 4.14 (0.98) & 6.53 (2.30) & 3.77 (0.24) & 14.18 (8.54) & \textcolor[HTML]{F3A11C}{\textbf{14.75}} (0.16) & \textcolor[HTML]{F3A11C}{\textbf{155.31}} (30.61) \\
 & $(64\times 8)$ & 10.89 (0.11) & 17.97 (2.40) & 42.78 (4.14) & 90.79 (1.14) & 127.42 (23.24) & 393.39 (36.01) \\
 & $(64\times 16)$ & 10.89 (0.11) & 21.45 (0.32) & 47.39 (0.51) & 90.75 (1.14) & 178.51 (2.17) & 446.64 (3.80) \\
 & $(64\times 32)$ & 10.89 (0.11) & 21.45 (0.32) & 47.39 (0.51) & 90.79 (1.14) & 178.53 (2.17) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & 2.82 (0.02) & 3.03 (0.03) & 3.40 (0.05) & 5.37 (0.08) & 20.13 (0.34) & 192.82 (2.13) \\
 & $(48\times 4)$ & 2.63 (0.04) & \textcolor[HTML]{b842f8}{\textbf{2.90}} (0.02) & \textcolor[HTML]{b842f8}{\textbf{3.35}} (0.05) & \textcolor[HTML]{b842f8}{\textbf{4.88}} (0.04) & \textcolor[HTML]{b842f8}{\textbf{18.22}} (0.34) & \textcolor[HTML]{b842f8}{\textbf{170.41}} (2.61) \\
 & $(48\times 8)$ & \textcolor[HTML]{b842f8}{\textbf{2.59}} (0.02) & 2.91 (0.03) & 3.48 (0.06) & 5.00 (0.08) & 22.75 (2.21) & 204.13 (10.48) \\
 & $(48\times 16)$ & 2.86 (0.05) & 4.49 (0.42) & 12.11 (1.38) & 34.57 (0.95) & 85.37 (1.15) & 315.88 (3.38) \\
 & $(48\times 32)$ & 309.89 (68.29) & 432.21 (100.78) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & 2.82 (0.01) & 3.10 (0.02) & 3.55 (0.04) & 5.86 (0.09) & 18.33 (0.22) & 139.92 (2.65) \\
 & $(48\times 4)$ & 2.77 (0.03) & 2.98 (0.04) & 3.36 (0.05) & \underline{4.62} (0.06) & \underline{11.84} (0.15) & \underline{106.27} (1.92) \\
 & $(48\times 8)$ & 2.67 (0.02) & 2.93 (0.02) & 3.30 (0.03) & \underline{4.14} (0.07) & \underline{8.34} (0.16) & \underline{94.64} (1.75) \\
 & $(48\times 16)$ & 2.59 (0.03) & \textcolor[HTML]{0080DB}{\textbf{2.89}} (0.02) & \textcolor[HTML]{0080DB}{\underline{\textbf{3.27}}} (0.04) & \textcolor[HTML]{0080DB}{\underline{\textbf{3.85}}} (0.08) & \textcolor[HTML]{0080DB}{\underline{\textbf{6.11}}} (0.23) & \textcolor[HTML]{0080DB}{\underline{\textbf{71.91}}} (2.27) \\
 & $(48\times 32)$ & \textcolor[HTML]{0080DB}{\textbf{2.56}} (0.02) & 2.97 (0.03) & 3.69 (0.37) & 5.41 (0.75) & 18.48 (9.83) & 127.12 (40.39) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\begin{table}[h!]
\caption{Prediction MSE (standard error) for different models and dimensions (\textbf{all entries multiplied by $10^2$}),  as in Table \ref{tab:model_l2}, but with true function $f_4(\bx) = \|\bx\|_1$. }
\label{tab:model_l1}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & \textcolor[HTML]{f85d42}{\textbf{0.27}} (0.05) & \textcolor[HTML]{f85d42}{\textbf{1.13}} (0.10) & \textcolor[HTML]{f85d42}{\textbf{10.17}} (0.35) & \textcolor[HTML]{f85d42}{\textbf{37.13}} (1.85) & \textcolor[HTML]{f85d42}{\textbf{99.88}} (1.09) & 548.76 (13.52) \\
 & $(64\times 4)$ & 0.28 (0.04) & 1.75 (0.14) & 30.22 (1.71) & 82.04 (3.08) & 133.30 (4.17) & 496.88 (9.66) \\
 & $(64\times 8)$ & 0.42 (0.06) & 1.57 (0.13) & 23.90 (1.51) & 66.98 (3.35) & 121.82 (2.87) & 456.16 (8.15) \\
 & $(64\times 16)$ & 1.32 (0.72) & 6.04 (2.20) & 25.98 (4.96) & 70.23 (5.71) & 140.03 (9.92) & 414.02 (13.79) \\
 & $(64\times 32)$ & 8.33 (0.05) & 16.51 (0.17) & 41.58 (0.37) & 82.60 (1.04) & 162.61 (1.65) & \textcolor[HTML]{f85d42}{\textbf{413.48}} (3.96) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.17}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{0.52}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{4.15}} (0.11) & \textcolor[HTML]{F3A11C}{\textbf{13.50}} (0.48) & 41.78 (0.50) & 243.57 (3.55) \\
 & $(64\times 4)$ & 1.80 (1.03) & 3.56 (1.97) & 8.25 (3.60) & 20.67 (6.79) & \textcolor[HTML]{F3A11C}{\textbf{39.53}} (1.24) & \textcolor[HTML]{F3A11C}{\textbf{212.75}} (21.52) \\
 & $(64\times 8)$ & 8.34 (0.04) & 15.03 (1.54) & 37.80 (3.56) & 82.86 (1.10) & 131.26 (14.51) & 385.28 (23.60) \\
 & $(64\times 16)$ & 8.41 (0.07) & 16.57 (0.19) & 41.67 (0.35) & 82.80 (1.10) & 163.75 (1.74) & 419.16 (3.81) \\
 & $(64\times 32)$ & 8.34 (0.04) & 16.55 (0.18) & 41.67 (0.35) & 82.82 (1.11) & 163.75 (1.78) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & \textcolor[HTML]{b842f8}{\underline{\textbf{0.09}}} (0.02) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.24}}} (0.02) & \textcolor[HTML]{b842f8}{\underline{\textbf{1.88}}} (0.07) & \textcolor[HTML]{b842f8}{\underline{\textbf{8.51}}} (0.27) & 37.98 (0.51) & 255.17 (3.74) \\
 & $(48\times 4)$ & \underline{0.11} (0.03) & \underline{0.32} (0.03) & \underline{2.33} (0.09) & \underline{9.63} (0.42) & \textcolor[HTML]{b842f8}{\textbf{37.01}} (0.75) & \textcolor[HTML]{b842f8}{\textbf{226.24}} (2.67) \\
 & $(48\times 8)$ & \underline{0.11} (0.03) & 0.46 (0.04) & 3.30 (0.37) & 11.98 (0.47) & 50.04 (4.32) & 256.49 (7.62) \\
 & $(48\times 16)$ & 1.00 (0.31) & 5.15 (0.64) & 16.36 (0.77) & 39.91 (1.18) & 95.05 (1.09) & 322.96 (2.98) \\
 & $(48\times 32)$ & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{5}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & \textcolor[HTML]{0080DB}{\textbf{0.12}} (0.03) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.32}}} (0.03) & \textcolor[HTML]{0080DB}{\underline{\textbf{2.29}}} (0.08) & \textcolor[HTML]{0080DB}{\underline{\textbf{10.36}}} (0.38) & 34.56 (0.60) & 191.70 (2.14) \\
 & $(48\times 4)$ & 0.13 (0.03) & 0.36 (0.03) & 2.99 (0.13) & 10.66 (0.30) & \textcolor[HTML]{0080DB}{\underline{\textbf{31.53}}} (0.47) & \underline{147.17} (2.06) \\
 & $(48\times 8)$ & 0.13 (0.03) & 0.44 (0.05) & 3.31 (0.09) & 11.13 (0.41) & \underline{32.31} (0.71) & \underline{111.10} (1.95) \\
 & $(48\times 16)$ & 0.20 (0.03) & 0.51 (0.03) & 3.65 (0.10) & 11.73 (0.43) & \underline{33.19} (0.68) & \textcolor[HTML]{0080DB}{\underline{\textbf{96.46}}} (1.77) \\
 & $(48\times 32)$ & 0.28 (0.06) & 0.76 (0.07) & 5.02 (1.44) & 13.70 (1.53) & 48.17 (17.41) & 185.06 (51.63) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\begin{table}[h!]
\caption{Prediction MSE (standard error) for different models and dimensions (\textbf{all entries multiplied by $10^2$}),  as in Table \ref{tab:model_l2}, but with true function $f_5(\bx) = \max(\|\bx-\boldsymbol{\mu}\|^2, \|\bx+ \boldsymbol{\mu}\|^2)$ for a randomly drawn $\boldsymbol{\mu}$ with entries from $\calN(0,1/d)$ and  $\sigma = 1$.}
\label{tab:model_piecewise_quadratic}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & 0.69 (0.22) & \textcolor[HTML]{f85d42}{\textbf{1.47}} (0.25) & \textcolor[HTML]{f85d42}{\textbf{8.36}} (0.28) & \textcolor[HTML]{f85d42}{\textbf{28.95}} (0.81) & \textcolor[HTML]{f85d42}{\textbf{89.41}} (2.08) & 572.06 (22.30) \\
 & $(64\times 4)$ & 0.82 (0.22) & 1.69 (0.14) & 21.19 (1.48) & 64.24 (2.92) & 113.19 (2.49) & 501.88 (10.62) \\
 & $(64\times 8)$ & \textcolor[HTML]{f85d42}{\textbf{0.67}} (0.11) & 2.25 (0.27) & 21.84 (1.21) & 56.80 (1.89) & 106.91 (3.94) & \textcolor[HTML]{f85d42}{\textbf{451.58}} (13.73) \\
 & $(64\times 16)$ & 0.95 (0.10) & 24.61 (14.34) & 26.81 (11.78) & 69.72 (18.03) & 167.82 (29.04) & 475.73 (20.16) \\
 & $(64\times 32)$ & 75.51 (19.85) & 98.36 (25.56) & 131.75 (13.79) & 164.71 (14.55) & 247.58 (8.99) & 509.14 (5.62) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.27}} (0.05) & \textcolor[HTML]{F3A11C}{\textbf{0.53}} (0.05) & \textcolor[HTML]{F3A11C}{\textbf{2.90}} (0.09) & \textcolor[HTML]{F3A11C}{\textbf{9.67}} (0.31) & 36.14 (0.72) & 237.50 (5.63) \\
 & $(64\times 4)$ & 22.64 (16.19) & 54.22 (30.72) & 4.50 (1.27) & 36.47 (25.71) & \textcolor[HTML]{F3A11C}{\textbf{32.66}} (1.54) & \textcolor[HTML]{F3A11C}{\textbf{205.72}} (35.20) \\
 & $(64\times 8)$ & 75.51 (19.85) & 84.54 (26.75) & 117.35 (16.28) & 165.32 (14.59) & 181.35 (29.24) & 458.21 (37.49) \\
 & $(64\times 16)$ & 75.56 (19.82) & 98.48 (25.63) & 131.81 (13.78) & 165.09 (14.57) & 249.28 (9.09) & 515.78 (5.77) \\
 & $(64\times 32)$ & 75.51 (19.85) & 98.48 (25.63) & 131.75 (13.77) & 165.13 (14.57) & 249.29 (9.12) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & \underline{0.17} (0.03) & 0.53 (0.05) & 2.62 (0.08) & 9.04 (0.27) & 32.70 (0.94) & 254.03 (3.53) \\
 & $(48\times 4)$ & \underline{0.13} (0.03) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.40}}} (0.03) & \textcolor[HTML]{b842f8}{\underline{\textbf{2.27}}} (0.07) & 8.31 (0.30) & \textcolor[HTML]{b842f8}{\textbf{31.29}} (0.52) & \textcolor[HTML]{b842f8}{\textbf{227.87}} (5.30) \\
 & $(48\times 8)$ & \textcolor[HTML]{b842f8}{\underline{\textbf{0.13}}} (0.03) & \underline{0.42} (0.03) & 2.64 (0.18) & \textcolor[HTML]{b842f8}{\textbf{8.28}} (0.23) & 40.57 (4.17) & 257.12 (10.49) \\
 & $(48\times 16)$ & 1.44 (0.59) & 10.72 (1.70) & 29.95 (4.30) & 55.89 (1.44) & 117.14 (2.70) & 363.39 (4.95) \\
 & $(48\times 32)$ & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{5}$ ($\sim 10^{5}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & 0.20 (0.03) & 0.61 (0.06) & 2.92 (0.10) & 8.58 (0.22) & 28.40 (0.66) & 184.15 (2.67) \\
 & $(48\times 4)$ & \textcolor[HTML]{0080DB}{\textbf{0.18}} (0.03) & 0.50 (0.03) & \underline{2.33} (0.07) & \textcolor[HTML]{0080DB}{\underline{\textbf{7.33}}} (0.19) & \underline{23.91} (0.59) & \underline{131.53} (1.50) \\
 & $(48\times 8)$ & 0.27 (0.06) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.44}}} (0.03) & 2.37 (0.11) & \underline{7.51} (0.31) & \textcolor[HTML]{0080DB}{\underline{\textbf{22.16}}} (0.60) & \underline{96.75} (1.75) \\
 & $(48\times 16)$ & 0.20 (0.04) & 0.45 (0.03) & \textcolor[HTML]{0080DB}{\underline{\textbf{2.08}}} (0.08) & \underline{7.56} (0.29) & \underline{22.32} (0.48) & \textcolor[HTML]{0080DB}{\underline{\textbf{74.75}}} (1.50) \\
 & $(48\times 32)$ & 0.24 (0.05) & 0.51 (0.08) & 3.67 (1.67) & 11.60 (2.64) & 42.20 (20.35) & 164.47 (52.20) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

%

\begin{table}[h!]
\caption{Prediction MSE (standard error) for different models and dimensions (\textbf{all entries multiplied by $10^2$}),  as in Table \ref{tab:model_l2}, but with true function $f_6(\bx) = \exp(\|\bx\|_1/\sqrt{d})$ with $\sigma = 1$.}
\label{tab:model_exp}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & \textcolor[HTML]{f85d42}{\textbf{0.36}} (0.06) & \textcolor[HTML]{f85d42}{\textbf{1.11}} (0.08) & \textcolor[HTML]{f85d42}{\textbf{9.94}} (0.56) & \textcolor[HTML]{f85d42}{\textbf{47.95}} (1.94) & \textcolor[HTML]{f85d42}{\textbf{250.08}} (3.94) & 11471.25 (349.59) \\
 & $(64\times 4)$ & 0.41 (0.04) & 2.28 (0.26) & 26.33 (1.52) & 91.29 (2.10) & 285.11 (5.21) & 10702.44 (173.90) \\
 & $(64\times 8)$ & 0.58 (0.10) & 2.22 (0.30) & 28.26 (1.60) & 89.18 (4.35) & 259.27 (7.61) & \textcolor[HTML]{f85d42}{\textbf{9582.89}} (290.28) \\
 & $(64\times 16)$ & 3.14 (2.19) & 9.17 (4.70) & 41.87 (11.90) & 125.34 (24.92) & 573.28 (87.54) & 10458.38 (537.45) \\
 & $(64\times 32)$ & 24.17 (0.16) & 37.46 (0.48) & 86.92 (1.10) & 218.91 (3.37) & 795.02 (9.97) & 11078.56 (134.77) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.23}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{0.60}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{5.86}} (0.25) & \textcolor[HTML]{F3A11C}{\textbf{27.52}} (0.62) & 150.64 (2.35) & 5451.47 (46.74) \\
 & $(64\times 4)$ & 4.99 (3.00) & 7.77 (4.53) & 6.97 (0.83) & 46.47 (19.13) & \textcolor[HTML]{F3A11C}{\textbf{126.86}} (1.19) & \textcolor[HTML]{F3A11C}{\textbf{4639.58}} (655.27) \\
 & $(64\times 8)$ & 24.18 (0.15) & 34.14 (3.51) & 78.38 (7.75) & 219.32 (3.48) & 591.78 (92.96) & 10395.42 (680.92) \\
 & $(64\times 16)$ & 24.24 (0.15) & 37.55 (0.50) & 87.05 (1.09) & 219.20 (3.48) & 799.24 (10.20) & 11201.37 (123.12) \\
 & $(64\times 32)$ & 24.18 (0.15) & 37.51 (0.49) & 87.05 (1.10) & 219.29 (3.45) & 799.24 (10.42) & $>10^{12}$ ($\sim 10^{12}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & \underline{0.15} (0.03) & \underline{0.41} (0.04) & \textcolor[HTML]{b842f8}{\underline{\textbf{2.44}}} (0.09) & \textcolor[HTML]{b842f8}{\underline{\textbf{12.37}}} (0.50) & 157.98 (3.14) & 5904.85 (68.08) \\
 & $(48\times 4)$ & \underline{0.12} (0.03) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.41}}} (0.02) & \underline{2.88} (0.09) & \underline{13.27} (0.77) & \textcolor[HTML]{b842f8}{\textbf{146.12}} (2.97) & \textcolor[HTML]{b842f8}{\textbf{5225.13}} (78.06) \\
 & $(48\times 8)$ & \textcolor[HTML]{b842f8}{\underline{\textbf{0.11}}} (0.03) & 0.51 (0.03) & \underline{3.95} (0.43) & \underline{16.65} (0.63) & 161.02 (9.06) & 6141.55 (241.40) \\
 & $(48\times 16)$ & 1.24 (0.36) & 7.54 (1.24) & 24.80 (1.57) & 80.59 (2.44) & 364.12 (4.04) & 8440.63 (86.10) \\
 & $(48\times 32)$ & $>10^3$ ($\sim 10^3$) & $>10^3$ ($\sim 10^3$) & $>10^3$ ($\sim 10^3$) & $>10^4$ ($\sim 10^4$) & $>10^3$ ($\sim 10^3$) & $>10^{6}$ ($\sim 10^{5}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & 0.20 (0.03) & 0.63 (0.10) & 4.15 (0.28) & 25.66 (1.32) & 165.49 (2.65) & 4624.00 (49.79) \\
 & $(48\times 4)$ & 0.17 (0.03) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.50}}} (0.04) & \textcolor[HTML]{0080DB}{\textbf{4.05}} (0.26) & \textcolor[HTML]{0080DB}{\textbf{21.42}} (0.40) & \underline{116.96} (2.16) & \underline{3461.44} (56.65) \\
 & $(48\times 8)$ & \textcolor[HTML]{0080DB}{\textbf{0.17}} (0.03) & 0.55 (0.04) & 4.74 (0.22) & 23.49 (0.71) & \underline{99.99} (1.27) & \underline{3108.10} (48.81) \\
 & $(48\times 16)$ & 0.17 (0.03) & 0.57 (0.04) & 5.35 (0.18) & 23.80 (0.86) & \textcolor[HTML]{0080DB}{\underline{\textbf{93.95}}} (1.45) & \textcolor[HTML]{0080DB}{\underline{\textbf{2577.29}}} (48.51) \\
 & $(48\times 32)$ & 0.21 (0.05) & 0.76 (0.08) & 7.31 (1.98) & 27.55 (3.13) & 186.48 (85.72) & 4475.24 (1090.57) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

%
\clearpage
\subsubsection{Interpolation across different dimensions for sample size $n = 5000$}\label{app:interpolation}

We additionally consider the noiseless interpolation setting ($\sigma = 0$) for the same collection of functions (a--f) across different dimensions $d \in \{1,2,5,10,20,50\}$ for a fixed sample size of $n = 5000$. The noiseless results are reported in \Cref{tab:model_noiseless_l2} ($f_1$), \Cref{tab:model_noiseless_l4} ($f_2$), \Cref{tab:model_noiseless_l1} ($f_4$), \Cref{tab:model_noiseless_piecewise_quadratic} ($f_5$), and \Cref{tab:model_noiseless_exp} ($f_6$). For $f_3$ the prediction MSE is already reported in the noiseless setting in \Cref{tab:model_quadratic_sinusoidal}. The observations are consistent with the noisy setting: HyCNNs outperform all other architectures, with the advantage being most pronounced in higher dimensions. Notably, in the noiseless setting, MLPs perform significantly better than ICNNs, which aligns with the theoretical considerations in \Cref{sec:approximation}, where we show that ReLU ICNNs suffer from limited expressivity due to a merely linear growth of linear pieces with depth.

\begin{table}[h!]
\caption{Prediction MSE and standard error (SE) by network and dimension (\textbf{all entries multiplied by $10^2$}; rounded to 2 decimal places) for learning the function $f_1(\bx) = \|\bx\|_2^2$ in the \emph{noiseless} setting ($\sigma = 0$). All other settings are as in \Cref{tab:model_l2}.}
\label{tab:model_noiseless_l2}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & $1.6\cdot 10^{-3}$ ($5.3\cdot 10^{-4}$) & \textcolor[HTML]{f85d42}{\textbf{0.01}} ($2.3\cdot 10^{-3}$) & \textcolor[HTML]{f85d42}{\textbf{0.20}} (0.01) & 3.00 (0.09) & 23.83 (0.69) & 395.98 (14.68) \\
 & $(64\times 4)$ & \underline{$3.3\cdot 10^{-4}$} ($2.1\cdot 10^{-4}$) & 0.02 (0.02) & 0.21 (0.03) & \textcolor[HTML]{f85d42}{\textbf{2.46}} (0.17) & \textcolor[HTML]{f85d42}{\textbf{22.85}} (0.51) & 352.80 (6.24) \\
 & $(64\times 8)$ & \textcolor[HTML]{f85d42}{\underline{$\mathbf{1.8\cdot 10^{-4}}$}} ($1.0\cdot 10^{-4}$) & 0.01 ($2.3\cdot 10^{-3}$) & 0.34 (0.12) & 2.49 (0.27) & 40.07 (13.62) & \textcolor[HTML]{f85d42}{\textbf{319.21}} (12.04) \\
 & $(64\times 16)$ & 0.91 (0.85) & 3.51 (2.20) & 14.56 (6.22) & 10.84 (7.89) & 67.92 (21.44) & 381.51 (25.62) \\
 & $(64\times 32)$ & 8.87 (0.07) & 17.71 (0.23) & 44.39 (0.41) & 88.11 (1.19) & 174.49 (1.96) & 440.28 (4.02) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{$\mathbf{1.8\cdot 10^{-3}}$} ($2.4\cdot 10^{-4}$) & \textcolor[HTML]{F3A11C}{\textbf{0.01}} ($1.2\cdot 10^{-3}$) & \textcolor[HTML]{F3A11C}{\textbf{0.27}} (0.01) & \textcolor[HTML]{F3A11C}{\textbf{2.49}} (0.05) & 17.63 (0.29) & 177.93 (2.46) \\
 & $(64\times 4)$ & 1.77 (1.11) & 3.48 (2.20) & 0.43 (0.22) & 10.66 (8.55) & \textcolor[HTML]{F3A11C}{\textbf{10.97}} (0.18) & \textcolor[HTML]{F3A11C}{\textbf{151.34}} (30.59) \\
 & $(64\times 8)$ & 8.87 (0.07) & 14.35 (2.28) & 39.92 (4.19) & 88.30 (1.20) & 124.57 (23.15) & 389.14 (36.78) \\
 & $(64\times 16)$ & 8.87 (0.06) & 17.73 (0.23) & 44.46 (0.40) & 88.27 (1.21) & 175.34 (2.06) & 443.96 (3.79) \\
 & $(64\times 32)$ & 8.87 (0.07) & 17.73 (0.23) & 44.46 (0.40) & 88.30 (1.20) & 175.37 (2.07) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & $1.8\cdot 10^{-3}$ ($5.8\cdot 10^{-4}$) & 0.01 ($7.7\cdot 10^{-4}$) & 0.14 (0.01) & 1.69 (0.04) & 16.64 (0.31) & 188.11 (2.06) \\
 & $(48\times 4)$ & $1.5\cdot 10^{-3}$ ($5.7\cdot 10^{-4}$) & \textcolor[HTML]{b842f8}{\textbf{0.01}} ($6.2\cdot 10^{-4}$) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.11}}} (0.01) & \textcolor[HTML]{b842f8}{\textbf{1.37}} (0.06) & \textcolor[HTML]{b842f8}{\textbf{14.57}} (0.39) & \textcolor[HTML]{b842f8}{\textbf{163.24}} (3.15) \\
 & $(48\times 8)$ & \textcolor[HTML]{b842f8}{$\mathbf{1.2\cdot 10^{-3}}$} ($1.4\cdot 10^{-4}$) & 0.01 ($6.1\cdot 10^{-4}$) & 0.18 (0.03) & 1.53 (0.05) & 18.81 (2.03) & 201.48 (10.95) \\
 & $(48\times 16)$ & 0.01 ($4.3\cdot 10^{-3}$) & 1.01 (0.41) & 8.21 (1.48) & 30.95 (1.10) & 81.62 (1.03) & 314.68 (3.06) \\
 & $(48\times 32)$ & 251.00 (55.69) & 354.88 (82.97) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & $8.1\cdot 10^{-4}$ ($1.5\cdot 10^{-4}$) & 0.01 ($1.4\cdot 10^{-3}$) & 0.21 (0.02) & 2.34 (0.08) & 14.31 (0.27) & 133.81 (1.98) \\
 & $(48\times 4)$ & $5.7\cdot 10^{-4}$ ($2.7\cdot 10^{-4}$) & \underline{$2.7\cdot 10^{-3}$} ($9.1\cdot 10^{-4}$) & 0.12 (0.05) & \underline{0.97} (0.02) & \underline{8.36} (0.12) & \underline{100.36} (1.77) \\
 & $(48\times 8)$ & $5.7\cdot 10^{-4}$ ($2.7\cdot 10^{-4}$) & \underline{$1.6\cdot 10^{-3}$} ($3.1\cdot 10^{-4}$) & \underline{0.04} ($1.6\cdot 10^{-3}$) & \underline{0.52} (0.01) & \underline{4.84} (0.11) & \underline{89.93} (1.86) \\
 & $(48\times 16)$ & \textcolor[HTML]{0080DB}{\underline{$\mathbf{2.2\cdot 10^{-4}}$}} ($4.9\cdot 10^{-5}$) & \textcolor[HTML]{0080DB}{\underline{$\mathbf{1.1\cdot 10^{-3}}$}} ($4.4\cdot 10^{-4}$) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.03}}} ($4.1\cdot 10^{-3}$) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.36}}} (0.10) & \textcolor[HTML]{0080DB}{\underline{\textbf{2.69}}} (0.19) & \textcolor[HTML]{0080DB}{\underline{\textbf{66.36}}} (1.30) \\
 & $(48\times 32)$ & $2.4\cdot 10^{-3}$ ($9.3\cdot 10^{-4}$) & 0.01 ($2.9\cdot 10^{-3}$) & 0.47 (0.38) & 2.00 (0.76) & 14.82 (9.77) & 121.92 (38.28) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\newpage

\begin{table}
\caption{Prediction MSE and standard error (SE) by network and dimension (\textbf{all entries multiplied by $10^2$}; rounded to 2 decimal places) for learning the function $f_2(\bx) = \|\bx\|_4^4$ in the \emph{noiseless} setting ($\sigma = 0$), as in \Cref{tab:model_noiseless_l2}.}
\label{tab:model_noiseless_l4}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & \textcolor[HTML]{f85d42}{\underline{$\mathbf{1.4\cdot 10^{-3}}$}} ($7.0\cdot 10^{-4}$) & 0.02 (0.01) & 0.56 (0.04) & \textcolor[HTML]{f85d42}{\textbf{8.82}} (0.25) & \textcolor[HTML]{f85d42}{\textbf{34.46}} (0.83) & 355.95 (13.25) \\
 & $(64\times 4)$ & 0.01 ($4.2\cdot 10^{-3}$) & \textcolor[HTML]{f85d42}{\textbf{$1.3\cdot 10^{-2}$}} ($3.2\cdot 10^{-3}$) & \textcolor[HTML]{f85d42}{\underline{\textbf{0.45}}} (0.04) & 9.45 (0.38) & 36.11 (0.71) & 325.59 (5.70) \\
 & $(64\times 8)$ & 0.28 (0.25) & 0.12 (0.07) & \underline{0.50} (0.05) & 15.74 (5.95) & 37.97 (2.06) & \textcolor[HTML]{f85d42}{\textbf{300.14}} (6.42) \\
 & $(64\times 16)$ & 0.71 (0.67) & 2.85 (1.73) & 18.14 (5.54) & 33.92 (9.58) & 77.63 (16.08) & 323.36 (13.15) \\
 & $(64\times 32)$ & 7.13 (0.08) & 14.34 (0.25) & 35.77 (0.40) & 70.65 (0.93) & 140.47 (1.97) & 351.77 (3.31) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\underline{$\mathbf{1.5\cdot 10^{-3}}$}} ($2.4\cdot 10^{-4}$) & \textcolor[HTML]{F3A11C}{\underline{\textbf{$8.5\cdot 10^{-3}$}}} ($8.4\cdot 10^{-4}$) & \textcolor[HTML]{F3A11C}{\textbf{0.56}} (0.06) & \textcolor[HTML]{F3A11C}{\textbf{7.63}} (0.12) & 25.90 (0.33) & 173.98 (3.08) \\
 & $(64\times 4)$ & 1.40 (0.89) & 2.85 (1.80) & 1.30 (0.17) & 14.23 (6.41) & \textcolor[HTML]{F3A11C}{\textbf{20.98}} (0.37) & \textcolor[HTML]{F3A11C}{\textbf{144.42}} (22.35) \\
 & $(64\times 8)$ & 7.13 (0.08) & 11.69 (1.86) & 32.36 (3.26) & 70.82 (0.95) & 104.92 (16.76) & 317.45 (24.60) \\
 & $(64\times 16)$ & 7.13 (0.08) & 14.36 (0.25) & 35.86 (0.40) & 70.80 (0.95) & 141.06 (2.02) & 354.30 (3.35) \\
 & $(64\times 32)$ & 7.13 (0.08) & 14.36 (0.25) & 35.86 (0.40) & 70.82 (0.95) & 141.10 (2.02) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & \textcolor[HTML]{b842f8}{\textbf{0.01}} ($1.5\cdot 10^{-3}$) & 0.02 ($1.1\cdot 10^{-3}$) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.54}}} (0.11) & 7.96 (0.16) & 26.55 (0.46) & 182.96 (2.42) \\
 & $(48\times 4)$ & 0.01 ($2.3\cdot 10^{-3}$) & \textcolor[HTML]{b842f8}{\textbf{0.02}} ($1.7\cdot 10^{-3}$) & 0.65 (0.09) & \textcolor[HTML]{b842f8}{\textbf{7.59}} (0.13) & \textcolor[HTML]{b842f8}{\textbf{24.01}} (0.42) & \textcolor[HTML]{b842f8}{\textbf{165.16}} (3.67) \\
 & $(48\times 8)$ & 0.01 ($7.1\cdot 10^{-4}$) & 0.04 ($2.6\cdot 10^{-3}$) & 1.05 (0.09) & 7.82 (0.11) & 29.02 (2.19) & 194.09 (6.24) \\
 & $(48\times 16)$ & 0.04 (0.01) & 0.92 (0.36) & 8.59 (0.95) & 28.54 (0.62) & 71.89 (0.89) & 267.27 (4.27) \\
 & $(48\times 32)$ & 205.24 (45.69) & 288.27 (66.90) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & $2.0\cdot 10^{-3}$ ($5.3\cdot 10^{-4}$) & 0.02 ($2.2\cdot 10^{-3}$) & 1.09 (0.09) & 8.82 (0.16) & 24.00 (0.41) & 137.74 (2.54) \\
 & $(48\times 4)$ & $2.0\cdot 10^{-3}$ ($9.9\cdot 10^{-4}$) & \underline{$8.1\cdot 10^{-3}$} ($1.7\cdot 10^{-3}$) & \textcolor[HTML]{0080DB}{\textbf{0.76}} (0.24) & \underline{6.99} (0.14) & \underline{18.69} (0.23) & \underline{106.29} (1.28) \\
 & $(48\times 8)$ & \textcolor[HTML]{0080DB}{\underline{$\mathbf{1.2\cdot 10^{-3}}$}} ($6.1\cdot 10^{-4}$) & \textcolor[HTML]{0080DB}{\underline{\textbf{$5.3\cdot 10^{-3}$}}} ($9.5\cdot 10^{-4}$) & 0.93 (0.04) & \underline{6.48} (0.09) & \underline{16.65} (0.28) & \underline{94.46} (1.56) \\
 & $(48\times 16)$ & $2.2\cdot 10^{-3}$ ($1.1\cdot 10^{-3}$) & $9.5\cdot 10^{-3}$ ($3.1\cdot 10^{-3}$) & 1.51 (0.06) & \textcolor[HTML]{0080DB}{\underline{\textbf{6.29}}} (0.13) & \textcolor[HTML]{0080DB}{\underline{\textbf{15.28}}} (0.22) & \textcolor[HTML]{0080DB}{\underline{\textbf{76.01}}} (1.18) \\
 & $(48\times 32)$ & $2.3\cdot 10^{-3}$ ($1.2\cdot 10^{-3}$) & 0.04 (0.01) & 2.38 (0.34) & 7.64 (0.67) & 25.36 (8.80) & 124.05 (33.68) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\begin{table}
\caption{Prediction MSE and standard error (SE) by network and dimension (\textbf{all entries multiplied by $10^2$}; rounded to 2 decimal places) for learning the function $f_4(\bx) = \|\bx\|_1$ in the \emph{noiseless} setting ($\sigma = 0$), as in \Cref{tab:model_noiseless_l2}.}
\label{tab:model_noiseless_l1}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & $2.3\cdot 10^{-3}$ ($1.0\cdot 10^{-3}$) & \textcolor[HTML]{f85d42}{\underline{$\mathbf{2.4\cdot 10^{-3}}$}} ($3.8\cdot 10^{-4}$) & \textcolor[HTML]{f85d42}{\textbf{0.05}} (0.01) & \textcolor[HTML]{f85d42}{\textbf{3.63}} (0.68) & \textcolor[HTML]{f85d42}{\textbf{33.71}} (0.72) & 410.02 (12.95) \\
 & $(64\times 4)$ & $3.5\cdot 10^{-3}$ ($1.6\cdot 10^{-3}$) & $4.9\cdot 10^{-3}$ ($1.4\cdot 10^{-3}$) & 0.16 (0.02) & 7.38 (0.26) & 36.56 (0.81) & 359.92 (9.23) \\
 & $(64\times 8)$ & 0.01 ($4.1\cdot 10^{-3}$) & 0.02 (0.01) & 0.36 (0.09) & 7.46 (0.35) & 35.87 (1.34) & \textcolor[HTML]{f85d42}{\textbf{340.10}} (13.85) \\
 & $(64\times 16)$ & \textcolor[HTML]{f85d42}{$\mathbf{2.3\cdot 10^{-3}}$} ($1.1\cdot 10^{-3}$) & 1.68 (1.56) & 13.43 (5.68) & 30.92 (10.72) & 122.71 (18.75) & 363.63 (21.54) \\
 & $(64\times 32)$ & 8.31 (0.05) & 16.50 (0.18) & 41.56 (0.37) & 82.59 (1.04) & 162.58 (1.64) & 413.48 (4.00) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.01}} ($4.3\cdot 10^{-4}$) & \textcolor[HTML]{F3A11C}{\textbf{0.07}} (0.01) & \textcolor[HTML]{F3A11C}{\textbf{0.34}} (0.03) & \textcolor[HTML]{F3A11C}{\textbf{5.70}} (0.27) & 27.64 (0.26) & 191.79 (3.78) \\
 & $(64\times 4)$ & 1.66 (1.05) & 3.26 (2.03) & 0.68 (0.31) & 11.91 (7.68) & \textcolor[HTML]{F3A11C}{\textbf{21.58}} (0.28) & \textcolor[HTML]{F3A11C}{\textbf{163.53}} (26.00) \\
 & $(64\times 8)$ & 8.31 (0.05) & 14.96 (1.58) & 37.41 (3.86) & 82.74 (1.03) & 119.67 (19.66) & 374.35 (29.63) \\
 & $(64\times 16)$ & 8.31 (0.05) & 16.52 (0.18) & 41.60 (0.37) & 82.72 (1.04) & 163.37 (1.70) & 417.46 (3.76) \\
 & $(64\times 32)$ & 8.31 (0.05) & 16.52 (0.18) & 41.61 (0.37) & 82.74 (1.04) & 163.39 (1.74) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & \textcolor[HTML]{b842f8}{\underline{$\mathbf{7.4\cdot 10^{-5}}$}} ($1.8\cdot 10^{-5}$) & \textcolor[HTML]{b842f8}{\underline{$\mathbf{5.4\cdot 10^{-4}}$}} ($7.7\cdot 10^{-5}$) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.01}}} ($1.8\cdot 10^{-3}$) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.10}}} (0.01) & 22.50 (0.87) & 204.57 (3.87) \\
 & $(48\times 4)$ & $2.7\cdot 10^{-4}$ ($7.8\cdot 10^{-5}$) & $4.9\cdot 10^{-3}$ ($1.1\cdot 10^{-3}$) & \underline{0.04} (0.01) & \underline{0.15} (0.02) & \textcolor[HTML]{b842f8}{\textbf{20.48}} (0.78) & \textcolor[HTML]{b842f8}{\textbf{178.75}} (3.03) \\
 & $(48\times 8)$ & \underline{$2.4\cdot 10^{-4}$} ($5.2\cdot 10^{-5}$) & 0.01 ($1.3\cdot 10^{-3}$) & 0.20 (0.07) & 0.64 (0.09) & 24.51 (2.13) & 208.05 (8.40) \\
 & $(48\times 16)$ & 0.02 (0.01) & 1.42 (0.45) & 9.80 (1.56) & 33.18 (1.24) & 82.83 (1.18) & 309.10 (1.77) \\
 & $(48\times 32)$ & 233.70 (51.54) & 332.26 (77.87) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & \textcolor[HTML]{0080DB}{\underline{$\mathbf{1.4\cdot 10^{-5}}$}} ($2.7\cdot 10^{-6}$) & 0.01 (0.01) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.02}}} ($1.2\cdot 10^{-3}$) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.34}}} (0.03) & 22.72 (0.34) & 151.35 (2.76) \\
 & $(48\times 4)$ & $2.8\cdot 10^{-4}$ ($1.9\cdot 10^{-4}$) & \textcolor[HTML]{0080DB}{\underline{$\mathbf{1.4\cdot 10^{-3}}$}} ($4.2\cdot 10^{-4}$) & 0.06 (0.04) & 0.60 (0.05) & \underline{17.94} (0.31) & \underline{116.45} (2.43) \\
 & $(48\times 8)$ & $1.7\cdot 10^{-3}$ ($1.3\cdot 10^{-3}$) & $3.4\cdot 10^{-3}$ ($6.5\cdot 10^{-4}$) & 0.05 ($3.1\cdot 10^{-3}$) & 1.21 (0.05) & \underline{15.52} (0.21) & \underline{100.83} (1.62) \\
 & $(48\times 16)$ & 0.01 ($2.3\cdot 10^{-3}$) & 0.02 (0.01) & 0.16 (0.03) & 2.41 (0.41) & \textcolor[HTML]{0080DB}{\underline{\textbf{14.15}}} (0.21) & \textcolor[HTML]{0080DB}{\underline{\textbf{82.19}}} (1.30) \\
 & $(48\times 32)$ & 0.03 (0.01) & 0.09 (0.02) & 1.05 (0.33) & 5.20 (0.76) & 24.90 (8.94) & 140.15 (38.47) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\begin{table}
\caption{Prediction MSE and standard error (SE) by network and dimension (\textbf{all entries multiplied by $10^2$}; rounded to 2 decimal places) for learning the function $f_5(\bx) = \max(\|\bx-\boldsymbol{\mu}\|_2^2, \|\bx+\boldsymbol{\mu}\|_2^2)$ in the \emph{noiseless} setting ($\sigma = 0$) based on $n = 5{,}000$ data points $\bX_i \sim \text{Unif}([-1,1]^d)$ and $Y_i = f_5(\bX_i)$, where $\boldsymbol{\mu} \in \RR^d$ has entries independently drawn from $\calN(0,1/d)$. All other settings are as in \Cref{tab:model_l2}.}
\label{tab:model_noiseless_piecewise_quadratic}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & \textcolor[HTML]{f85d42}{\textbf{0.01}} ($2.7\cdot 10^{-3}$) & \textcolor[HTML]{f85d42}{\textbf{0.04}} (0.03) & \textcolor[HTML]{f85d42}{\textbf{0.32}} (0.03) & 3.69 (0.24) & 28.01 (0.58) & 422.95 (16.82) \\
 & $(64\times 4)$ & 0.02 (0.01) & 0.07 (0.04) & 0.33 (0.05) & 3.82 (0.50) & \textcolor[HTML]{f85d42}{\textbf{26.36}} (1.22) & 364.77 (9.32) \\
 & $(64\times 8)$ & 0.06 (0.04) & 0.11 (0.05) & 0.70 (0.18) & \textcolor[HTML]{f85d42}{\textbf{3.20}} (0.23) & 28.13 (1.97) & \textcolor[HTML]{f85d42}{\textbf{331.43}} (9.00) \\
 & $(64\times 16)$ & 0.07 (0.06) & 7.40 (6.90) & 10.01 (7.97) & 3.29 (0.21) & 44.71 (17.53) & 366.81 (32.00) \\
 & $(64\times 32)$ & 75.47 (19.84) & 98.34 (25.57) & 131.72 (13.80) & 164.70 (14.55) & 247.61 (9.02) & 509.12 (5.66) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.04}} (0.01) & \textcolor[HTML]{F3A11C}{\textbf{0.08}} (0.02) & \textcolor[HTML]{F3A11C}{\textbf{0.54}} (0.04) & \textcolor[HTML]{F3A11C}{\textbf{3.05}} (0.11) & 19.87 (0.36) & 196.04 (2.89) \\
 & $(64\times 4)$ & 22.42 (16.23) & 46.00 (31.06) & 1.24 (0.73) & 29.86 (26.37) & \textcolor[HTML]{F3A11C}{\textbf{12.62}} (0.32) & \textcolor[HTML]{F3A11C}{\textbf{168.85}} (38.60) \\
 & $(64\times 8)$ & 75.46 (19.85) & 81.91 (27.46) & 116.40 (16.85) & 165.12 (14.57) & 171.96 (33.34) & 448.62 (42.81) \\
 & $(64\times 16)$ & 75.46 (19.83) & 98.45 (25.65) & 131.77 (13.81) & 164.98 (14.57) & 248.85 (9.13) & 514.14 (5.59) \\
 & $(64\times 32)$ & 75.46 (19.84) & 98.48 (25.67) & 131.70 (13.79) & 165.03 (14.56) & 248.87 (9.15) & $>10^{11}$ ($\sim 10^{11}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & 0.01 (0.01) & 0.03 (0.01) & 0.35 (0.03) & 2.56 (0.11) & 19.07 (0.63) & 202.26 (3.89) \\
 & $(48\times 4)$ & \underline{$3.5\cdot 10^{-3}$} ($1.4\cdot 10^{-3}$) & \textcolor[HTML]{b842f8}{\textbf{0.02}} (0.01) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.21}}} (0.02) & \textcolor[HTML]{b842f8}{\textbf{1.89}} (0.08) & \textcolor[HTML]{b842f8}{\textbf{16.53}} (0.37) & \textcolor[HTML]{b842f8}{\textbf{178.81}} (3.26) \\
 & $(48\times 8)$ & \textcolor[HTML]{b842f8}{\underline{$\mathbf{3.4\cdot 10^{-3}}$}} ($1.0\cdot 10^{-3}$) & 0.02 (0.01) & 0.37 (0.10) & 2.08 (0.12) & 19.48 (1.94) & 214.33 (11.86) \\
 & $(48\times 16)$ & 0.11 (0.08) & 3.54 (0.92) & 20.19 (5.00) & 45.28 (2.75) & 104.93 (2.80) & 348.18 (3.93) \\
 & $(48\times 32)$ & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) & $>10^{5}$ ($\sim 10^{4}$) & $>10^{4}$ ($\sim 10^{3}$) & $>10^{4}$ ($\sim 10^{4}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & $4.9\cdot 10^{-3}$ ($1.2\cdot 10^{-3}$) & 0.05 (0.02) & 0.58 (0.10) & 2.74 (0.09) & 15.89 (0.22) & 142.98 (1.82) \\
 & $(48\times 4)$ & \textcolor[HTML]{0080DB}{\underline{$\mathbf{3.0\cdot 10^{-3}}$}} ($1.2\cdot 10^{-3}$) & \underline{0.02} (0.01) & 0.27 (0.10) & \underline{1.23} (0.05) & \underline{9.29} (0.16) & \underline{107.41} (1.61) \\
 & $(48\times 8)$ & 0.02 (0.02) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.01}}} ($3.2\cdot 10^{-3}$) & \underline{0.10} (0.01) & \underline{0.72} (0.03) & \underline{5.52} (0.13) & \underline{99.11} (2.45) \\
 & $(48\times 16)$ & 0.02 (0.01) & \underline{0.02} (0.01) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.08}}} (0.01) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.51}}} (0.12) & \textcolor[HTML]{0080DB}{\underline{\textbf{3.38}}} (0.21) & \textcolor[HTML]{0080DB}{\underline{\textbf{75.61}}} (2.58) \\
 & $(48\times 32)$ & 0.05 (0.02) & 0.11 (0.06) & 1.03 (0.74) & 4.05 (1.77) & 19.90 (13.38) & 136.98 (39.51) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\begin{table}
\caption{Prediction MSE and standard error (SE) by network and dimension (\textbf{all entries multiplied by $10^2$}; rounded to 2 decimal places) for learning the function $f_6(\bx) = \exp(\|\bx\|_1/\sqrt{d})$ in the \emph{noiseless} setting ($\sigma = 0$), as in \Cref{tab:model_noiseless_l2}.}
\label{tab:model_noiseless_exp}
\scriptsize
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\multicolumn{2}{c}{Network $\backslash$ $d$} & 1 & 2 & 5 & 10 & 20 & 50 \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{MLP}} & $(64\times 2)$ & $4.9\cdot 10^{-3}$ ($3.0\cdot 10^{-3}$) & \textcolor[HTML]{f85d42}{\textbf{0.02}} ($4.9\cdot 10^{-3}$) & \textcolor[HTML]{f85d42}{\textbf{0.23}} (0.02) & \textcolor[HTML]{f85d42}{\textbf{19.07}} (1.31) & 193.26 (5.24) & $1.1\cdot 10^{4}$ (350.64) \\
 & $(64\times 4)$ & \textcolor[HTML]{f85d42}{$\mathbf{3.2\cdot 10^{-3}}$} ($1.8\cdot 10^{-3}$) & 0.03 (0.01) & 0.44 (0.03) & 23.76 (0.81) & 203.70 (7.37) & $1.0\cdot 10^{4}$ (223.95) \\
 & $(64\times 8)$ & 0.01 ($3.7\cdot 10^{-3}$) & 0.04 (0.02) & 0.48 (0.05) & 22.67 (0.66) & \textcolor[HTML]{f85d42}{\textbf{189.32}} (4.21) & \textcolor[HTML]{f85d42}{$\mathbf{9.5\cdot 10^{3}}$} (258.31) \\
 & $(64\times 16)$ & 0.02 (0.01) & 5.46 (3.66) & 34.74 (13.15) & 83.05 (28.67) & 619.84 (89.93) & $1.0\cdot 10^{4}$ (483.55) \\
 & $(64\times 32)$ & 24.14 (0.16) & 37.44 (0.49) & 86.90 (1.10) & 218.89 (3.38) & 794.99 (9.96) & $1.1\cdot 10^{4}$ (134.94) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{ICNN}} & $(64\times 2)$ & \textcolor[HTML]{F3A11C}{\textbf{0.01}} ($9.4\cdot 10^{-4}$) & \textcolor[HTML]{F3A11C}{\textbf{0.05}} ($4.4\cdot 10^{-3}$) & \textcolor[HTML]{F3A11C}{\textbf{0.44}} (0.03) & \textcolor[HTML]{F3A11C}{\textbf{17.38}} (0.38) & 139.84 (2.12) & $5.5\cdot 10^{3}$ (82.55) \\
 & $(64\times 4)$ & 4.80 (3.03) & 7.34 (4.62) & 0.93 (0.38) & 34.78 (20.34) & \textcolor[HTML]{F3A11C}{\textbf{110.74}} (1.05) & \textcolor[HTML]{F3A11C}{$\mathbf{4.6\cdot 10^{3}}$} (655.17) \\
 & $(64\times 8)$ & 24.14 (0.16) & 30.36 (4.79) & 78.07 (8.00) & 219.25 (3.39) & 592.39 (92.56) & $10.0\cdot 10^{3}$ (848.32) \\
 & $(64\times 16)$ & 24.15 (0.16) & 37.51 (0.49) & 87.02 (1.09) & 219.21 (3.42) & 799.00 (10.23) & $1.1\cdot 10^{4}$ (122.76) \\
 & $(64\times 32)$ & 24.14 (0.16) & 37.50 (0.49) & 87.02 (1.09) & 219.27 (3.38) & 799.00 (10.44) & $>10^{12}$ ($\sim 10^{12}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{GMN}} & $(48\times 2)$ & $2.8\cdot 10^{-3}$ ($1.0\cdot 10^{-3}$) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.01}}} ($1.2\cdot 10^{-3}$) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.10}}} (0.01) & \textcolor[HTML]{b842f8}{\underline{\textbf{0.73}}} (0.05) & 133.27 (4.28) & $5.8\cdot 10^{3}$ (95.85) \\
 & $(48\times 4)$ & \underline{$1.6\cdot 10^{-3}$} ($3.3\cdot 10^{-4}$) & 0.02 ($3.5\cdot 10^{-3}$) & \underline{0.15} (0.02) & \underline{0.94} (0.14) & \textcolor[HTML]{b842f8}{\textbf{123.09}} (3.58) & \textcolor[HTML]{b842f8}{$\mathbf{5.3\cdot 10^{3}}$} (79.35) \\
 & $(48\times 8)$ & \textcolor[HTML]{b842f8}{\underline{$\mathbf{1.3\cdot 10^{-3}}$}} ($2.6\cdot 10^{-4}$) & 0.02 ($2.2\cdot 10^{-3}$) & 0.48 (0.12) & \underline{2.53} (0.21) & 133.35 (8.55) & $6.1\cdot 10^{3}$ (265.13) \\
 & $(48\times 16)$ & 0.02 (0.01) & 2.21 (0.82) & 15.46 (2.56) & 70.63 (2.55) & 351.98 (5.10) & $8.5\cdot 10^{3}$ (89.60) \\
 & $(48\times 32)$ & 680.39 (150.66) & 756.01 (176.80) & $2.6\cdot 10^{3}$ ($1.2\cdot 10^{3}$) & $1.5\cdot 10^{4}$ ($9.4\cdot 10^{3}$) & $7.9\cdot 10^{3}$ ($1.5\cdot 10^{3}$) & $>10^{6}$ ($\sim 10^{5}$) \\
\midrule
\multirow{5}{*}{\rotatebox[origin=c]{90}{HyCNN}} & $(48\times 2)$ & $2.7\cdot 10^{-3}$ ($3.0\cdot 10^{-4}$) & 0.02 ($3.0\cdot 10^{-3}$) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.18}}} (0.02) & 4.45 (0.92) & 152.21 (2.17) & $4.6\cdot 10^{3}$ (81.86) \\
 & $(48\times 4)$ & \textcolor[HTML]{0080DB}{\underline{$\mathbf{1.8\cdot 10^{-3}}$}} ($7.8\cdot 10^{-4}$) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.01}}} ($1.6\cdot 10^{-3}$) & 0.37 (0.22) & \textcolor[HTML]{0080DB}{\textbf{3.34}} (0.23) & \underline{101.45} (1.45) & \underline{$3.5\cdot 10^{3}$} (66.26) \\
 & $(48\times 8)$ & $2.6\cdot 10^{-3}$ ($1.4\cdot 10^{-3}$) & \underline{0.01} ($1.8\cdot 10^{-3}$) & 0.22 (0.01) & 6.27 (0.24) & \underline{83.71} (1.77) & \underline{$3.1\cdot 10^{3}$} (41.87) \\
 & $(48\times 16)$ & $3.8\cdot 10^{-3}$ ($1.6\cdot 10^{-3}$) & 0.03 (0.01) & 0.52 (0.08) & 9.90 (0.67) & \textcolor[HTML]{0080DB}{\underline{\textbf{74.66}}} (1.19) & \textcolor[HTML]{0080DB}{\underline{$\mathbf{2.6\cdot 10^{3}}$}} (56.03) \\
 & $(48\times 32)$ & 0.02 (0.01) & 0.13 (0.02) & 2.50 (0.86) & 17.63 (2.59) & 158.06 (70.01) & $4.6\cdot 10^{3}$ ($1.1\cdot 10^{3}$) \\
\bottomrule
\end{tabular}%
}%
}
\end{table}

\newpage

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%

\clearpage

\subsection{HyCNN-based OT map estimation}\label{app:OT_experiments}\label{app:OT_implementation}

We provide additional experimental results and implementation details complementing the optimal transport map estimation experiments described in \Cref{sec:experiments}. The training procedure for HyCNN-based OT map estimation, based on the saddle-point formulation \eqref{eq:HyCNN_OT_potential_estimation}, is summarized in \Cref{alg:HyCNN_ot}.

As in the regression experiments of \Cref{app:regression_experiments}, for the HyCNN potential $f_{\theta_f}$ we do not parameterize the hidden-to-hidden weight matrices $V_\ell^{k}$ directly but through an unconstrained matrix $R_\ell^{k} \in \RR^{n_{\ell+1}\times n_\ell}$, via the entrywise softplus reparametrization $V_\ell^{k} = \operatorname{softplus}(R_\ell^{k}) = \log(1+\exp(R_\ell^{k}))$. Since $\operatorname{softplus}\colon \RR \to (0,\infty)$ is smooth and bijective onto the positive reals, the effective weights $V_\ell^{k}$ are strictly positive on every forward pass, so that input-convexity of $f_{\theta_f}$ in its argument is preserved throughout training; at the same time, Adam updates are applied to the unconstrained $R_\ell^{k}$, i.e.\ the gradient computation uses $\partial V_\ell^{k} / \partial R_\ell^{k}$ and flows back to $R_\ell^{k}$ without requiring any explicit projection onto the non-negative orthant. This way, the full set of parameters of $f_{\theta_f}$ can be trained with standard unconstrained optimizers and standard PyTorch autodiff, while the architectural constraint $V_\ell^{k} \geq 0$ is satisfied exactly by construction.

\begin{algorithm}[h!]
 \caption{HyCNN Optimal Transport Map Learning}
 \label{alg:HyCNN_ot}
 \begin{algorithmic}
   \STATE {\bfseries Input:} data $(\bx_i)_{i=1}^n$ from source $P$, data $(\by_j)_{j=1}^m$ from target $Q$, batch size $M$, inner and outer loop iterations $S,T\in \NN$, HyCNN potential $f_{\theta_f} \in \texttt{HyCNN}_\tau(\RR^d)$ and HyCNN critic $g_{\theta_g} \in \texttt{HyCNN}_\tau(\RR^d)$.
   \STATE Initialize $\theta_f$ and $\theta_g$ according to \Cref{sec:trainingHyCNNs}.
   \FOR{$t=1$ {\bfseries to} $T$}
       \STATE Sample mini-batch $(\bX_i)_{i=1}^M$ from $(\bx_i)_{i=1}^n$.
       \FOR{$s=1$ {\bfseries to} $S$}
           \STATE Sample mini-batch $(\bY_j)_{j=1}^M$ from $(\by_j)_{j=1}^m$.
           \STATE Update $\theta_g$ to minimize $\textstyle\frac{1}{M}\sum_{i=1}^{M} \Big[ f_{\theta_f}(\bX_i)+\langle \bY_i, \nabla g_{\theta_g}(\bY_i)\rangle - f_{\theta_f}(\nabla g_{\theta_g}(\bY_i)) \Big]$ with Adam.
        %
       \ENDFOR
       \STATE Update $\theta_f$ to maximize $\textstyle\frac{1}{M}\sum_{i=1}^{M} \Big[f_{\theta_f}(\bX_i)+\langle \bY_i, \nabla g_{\theta_g}(\bY_i)\rangle - f_{\theta_f}(\nabla g_{\theta_g}(\bY_i)) \Big]$ using Adam.
    %
   \ENDFOR
   \STATE {\bfseries Output:} {Estimated optimal transport map $\hat T\coloneqq \nabla \hat \phi$, where $\hat\phi = f_{\theta_f}$.}
 \end{algorithmic}
\end{algorithm}

\parabold{Network architectures}
Both the potential $f_{\theta_f}$ and the critic $g_{\theta_g}$ are parameterized by HyCNNs with the smooth log-sum-exp activation function $\overline\sigma_\tau$ from \eqref{eq:logsumexp}, using the same architecture (width and depth).

\parabold{Training}
For all experiments, we use the Adam optimizer \citep{kingma2014adam} with $\beta_1 = 0.5$ and $\beta_2 = 0.9$ and identical initial learning rate $\lambda = 10^{-2}$ for both $\theta_f$ and $\theta_g$. The learning rate follows a cosine decay schedule $\lambda_t = \lambda_{\min} + \tfrac{1}{2}(\lambda - \lambda_{\min})(1 + \cos(\pi t / T))$ with final ratio $\lambda_{\min}/\lambda = 0.01$. After each outer update, the weight matrices $V_\ell^j$ in $\theta_f$ are projected onto the non-negative orthant to ensure convexity of $f_{\theta_f}$. 

Notably, unlike the ICNN–based neural OT method by \cite{makkuva2020optimal}, we do not allow the hidden-to-hidden weight matrices $V_\ell^j$ in the critic network to have negative entries, as we found that it degrades performance of HyCNN based OT map estimation in high-dimensional settings. 

\parabold{Training in low dimensions} 
While discontinuities of the OT map can occur in any dimension, in low dimensions it is crucial to accurately resolve these discontinuities, as they have a pronounced effect on the quality of the estimated map. This requires the HyCNN to operate close to the maximum activation gating function (i.e., $\tau \to 0$ in the log-sum-exp activation $\overline\sigma_\tau$). However, training with small $\tau$ is challenging because the $\max$ operator may select a single gate per layer, so that only the weights associated with the active gate receive gradient updates while the remaining gates are not trained. To address this, we employ a cyclic cosine annealing schedule for the smoothness parameter $\tau$, that is, we start from $\tau_0 = 1$ and then periodically oscillate $\tau$ between large and small values and decrease per cycle by a fixed decay factor. 

During phases of large $\tau$, the smooth log-sum-exp activation distributes gradients across all gates, ensuring that all weight matrices are updated. During phases of small $\tau$, the network sharpens toward the piecewise-affine $\max$ regime needed to represent discontinuous maps.

\parabold{Training in moderate and high dimensions}
In higher dimensions ($d \geq 10$), recovering the OT map is already more involved, and empirically larger values of $\tau$ yielded better performance. We therefore use a fixed smoothness parameter $\tau$ without the cyclic cosine schedule in these settings. 

\subsubsection{OT map estimation in dimension $d = 2$}\label{app:OT_dim2}

For the two-dimensional OT visualization experiments, we consider the following examples \begin{enumerate}
    \item[$(i)$] five-component checkerboard (source) to four-component checkerboard (target), 
    \item[$(ii)$] standard normal (source) to half-moon (target),
    \item[$(iii)$] shifted half-moon (source) to shifted rotated half-moon (target), and 
    \item[$(iv)$] standard Gaussian (source) to a mixture of eight Gaussians arranged in a ring (target). 
\end{enumerate}
In Figure \ref{fig:HyCNN_OT_shapes_2d} we depict the training samples from the source distribution and target distribution as well as the pushforward of the source training samples under the learned HyCNN OT map $\nabla f$. In Figure \ref{fig:HyCNN_OT_shapes_2d_reverse} we show the pushforward of the target training samples under the learned gradient of the critic $g$, which corresponds to the reverse OT map. In Figure \ref{fig:HyCNN_OT_shapes_2d_potential} we visualize the learned potential $f$ and $g$ for the four examples using a contour plot. Throughout these examples, we observe that HyCNNs are capable to learn the correct target distribution (and thus the correct OT map) even in the presence of discontinuities. 

For the architecture we use HyCNNs with width $48$ and depth $4$ for both the potential $f$ and the critic $g$. We draw $n = m = M = 2000$ data points from the source and target distributions. The training consists of $T = 2500$ outer iterations for learning $f$, with $S = 5$ inner gradient steps per outer iteration for updating the critic $g$. The learning rate follows a cosine decay schedule with initial learning rate $\lambda = 10^{-2}$ and final ratio $\lambda_{\min}/\lambda = 0.01$. The smoothness parameter $\tau$ for the log-sum-exp activation is also decayed, we start with $\tau = 1$, and within a cycle of $100$ outer iterations, we decay the smoothness parameter $\tau$ by a factor of $0.8$ per cycle, with a cosine decaying schedule and ensure that by iteration $70\%$ of the cycle, $\tau$ has decayed to $0.1$ times its initial value in the cycle. Overall, this ensures that $\tau$ reaches a small value of $0.8^{24} \cdot 0.1 = 0.00047$ by the end of training, which allows the network to sharpen toward the piecewise-affine $\max$ regime needed to represent discontinuous maps, while also ensuring that all gates receive gradient updates during training.

%

%

%
%
%

%

\begin{figure}[t!]
    \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim=0 0 0 0, clip]{../figures/combined_sweep_reverse.pdf}}
        \caption{Reverse OT map estimation in dimension $d=2$. Each panel shows the pushforward of the target distribution under the learned reverse HyCNN OT map (width $48$, depth $4$), trained with $n = m = M = 2000$ data points, $T = 2500$ outer iterations, and $S = 5$ inner steps, using Adam with cosine-decayed learning rate ($\lambda = 10^{-2}$, final ratio $0.01$) and smoothness parameter $\tau_0 = 1$ (cosine decay). From left to right: (i) five-component checkerboard $\to$ four-component checkerboard, (ii) standard normal $\to$ half-moon, (iii) shifted half-moon $\to$ shifted rotated half-moon, (iv) standard Gaussian $\to$ mixture of eight Gaussians.}
         \label{fig:HyCNN_OT_shapes_2d_reverse}
         \end{center}
\end{figure}

\begin{figure}[t!]
    \begin{center}
    \centerline{\includegraphics[width=\textwidth, trim=0 0 0 0, clip]{../figures/combined_potential_contours.pdf}}
        \caption{Contour plots of the learned OT potential $\hat\phi$ in dimension $d=2$. Each panel shows the contour lines of the HyCNN potential (width $48$, depth $4$) learned from $n = m = M = 2000$ data points for the same collection of source--target pairs as in \Cref{fig:HyCNN_OT_shapes_2d_reverse}.} %
         \label{fig:HyCNN_OT_shapes_2d_potential}
         \end{center}
\end{figure}

%
%
%
%
%
%
%

%

%

%
%
%
%
%
%
%

\subsubsection{OT map estimation across different dimensions for sample sizes $n =5000$}\label{app:OT_dimensions}

In the following, we present detailed performance tables for the OT map estimation experiments described in \Cref{sec:experiments}. In total, we consider the following OT potentials with corresponding OT maps, 
\begin{align*}
    &\textstyle \text{(a) } \textstyle\phi_1(\bx) = \frac{\|\bx\|^2_2}{2}, && T_1(\bx) = \bx, \\ &\text{(b) } \textstyle\phi_2(\bx) = \frac{1}{2}\sum_{i = 1}^{d} \big(1+ \frac{\sin(i)}{2}\big)x_i^2, 
    && T_2(\bx) = \textstyle\big((1+ \frac{\sin(i)}{2})x_i\big)_{i \in [d]},\\
    &\textstyle \text{(c) } \textstyle\phi_3(\bx) = \frac{\|\bx\|^2_2}{2}+ \|\bx\|_1,&& T_3(\bx) = \big(x_i + \textup{sign}(x_i)\big)_{i \in [d]},\\
    &\text{(d) } \textstyle\phi_4(\bx) = \|\bx\|^4_4,&& T_4(\bx) = \big(4x_i^3\big)_{i\in [d]}.
\end{align*}

we report the prediction MSE of the estimated OT map $\hat T = \nabla \hat \phi$ against the ground-truth OT map $\overline T = \nabla \phi_\ell$ for dimension $d = 50$. The source distribution is $P = \calN(0, I_d)$ for (a--c) and $P = \text{Unif}[-1,1]^d$ for (d), and the target distribution is $Q = (\nabla \phi_\ell)_\# P$. We use $n = m = 5000$ independent samples from $P$ and $Q$, respectively. The MSE is defined as the average squared Euclidean distance between the estimated and ground-truth OT map evaluated on an independent test set, i.e., $$\text{MSE}_{\text{pred}} = \frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} \|\hat T(\bX_i) - \overline T(\bX_i)\|_2^2.$$

The test set consists of $N_{\text{test}} = 1{,}000$ independent samples from $P$ and $Q$. Results are averaged over $10$ independent runs with different random seeds for sample generation and network initialization. The training uses batch size $M = 256$, $T = 1{,}000$ outer iterations, $S = 5$ inner steps, learning rate $\lambda = 10^{-2}$ with cosine decay with final ratio $0.01$. The Adam optimizer uses $\beta_1 = 0.5$, $\beta_2 = 0.9$ for both the potential and critic networks.

We compare the HyCNN-based estimator (width $48$, depths $L \in \{2,4,6\}$, logsumexp smoothness $\tau \in \{0.1, 1, 10\}$) with the entropic optimal transport map estimator (regularization parameter $\epsilon = 0.1, 1, 10$), several ICNN variants (width $64$, depths $L \in \{2, 4, 6\}$, softplus smoothness $\tau \in \{0.1, 1, 10\}$) and the Monge Gap MLP estimator (width $64$, depths $L \in \{2, 4, 6\}$).

\parabold{Entropic OT baseline} As a non-parametric baseline we consider the entropic OT (EOT) map estimator \citep{seguy2017large,pooladian2021entropic}. Given independent samples $(\bX_i)_{i=1}^{n} \sim P$ and $(\bY_j)_{j=1}^{m} \sim Q$, let $\hat P_n = \frac{1}{n}\sum_i \delta_{\bX_i}$ and $\hat Q_m = \frac{1}{m}\sum_j \delta_{\bY_j}$ denote the empirical measures. The estimator solves the discrete entropic OT problem with squared-Euclidean cost $c(\bx,\by) = \tfrac{1}{2}\|\bx-\by\|_2^2$,
\begin{align}\label{eq:eot_primal}
\min_{\pi \in \Pi(\hat P_n, \hat Q_m)}\; \textstyle\sum_{i,j} \pi_{ij}\, c(\bX_i, \bY_j) + \varepsilon\, \mathrm{KL}\big(\pi\;\big\|\; \tfrac{1}{n}\mathbf{1}\otimes \tfrac{1}{m}\mathbf{1}\big),
\end{align}
with regularization parameter $\varepsilon \in \{0.1, 1, 10\}$, via log-domain Sinkhorn iterations until convergence. From the dual potential $g^\star$ associated with $\hat Q_m$, the out-of-sample \emph{barycentric} OT map is evaluated on any source sample via
\begin{align*}
\hat T_{\varepsilon}(\bx) = \sum_{j=1}^{m} w_j^{\varepsilon}(\bx)\, \bY_j, \qquad w_j^{\varepsilon}(\bx) = \frac{\exp\!\big(\big(g^\star(\bY_j) - c(\bx, \bY_j)\big)/\varepsilon\big)}{\sum_{j'=1}^{m} \exp\!\big(\big(g^\star(\bY_{j'}) - c(\bx, \bY_{j'})\big)/\varepsilon\big)}.
\end{align*}
On fresh test points $\tilde \bx \notin \{\bX_i\}_{i=1}^n$ we extend $\hat T_\varepsilon$ canonically to the whole ambient space as suggested by \cite{pooladian2021entropic} by 
\begin{align*}
\hat T_\varepsilon(\tilde \bx) =\sum_{j=1}^{m} w_j^{\varepsilon}(\tilde \bx)\, \bY_j, \qquad w_j^{\varepsilon}(\tilde \bx) = \frac{\exp\!\big(\big(g^\star(\bY_j) - c(\tilde \bx, \bY_j)\big)/\varepsilon\big)}{\sum_{j'=1}^{m} \exp\!\big(\big(g^\star(\bY_{j'}) - c(\tilde \bx, \bY_{j'})\big)/\varepsilon\big)}.
\end{align*}
%
%
%
%
%
The Sinkhorn problem itself and the dual potential $g^\star$ are computed with the \texttt{geomloss} package \citep{feydy2019interpolating} using the tensorized backend, squared-Euclidean cost, blur parameter $\sqrt{\varepsilon}$, and no debiasing.

\parabold{ICNN-based baselines}
We compare the HyCNN-based estimator against four ICNN variants, which we collectively refer to as \emph{ICNN-based methods}. All variants share the general ICNN template of \eqref{eq:ICNN}, i.e., hidden activations
\[
\bz_{\ell+1} = \sigma_\ell\big(V_\ell \bz_\ell + W_\ell \bx + \bb_\ell\big), \qquad \ell = 0,\dots,L-1,
\]
with scalar output $\operatorname{ICNN}(\bx) = V_L \bz_L + W_L \bx + \bb_L$, and differ only in their first-layer parameterization and choice of activation $\sigma_\ell$.
\begin{enumerate}
    \item[$(i)$] \textit{ICNN (ReLU).} The standard ICNN with first layer $\bz_1 = \sigma(W_0 \bx + \bb_0)$ and ReLU activation function $\sigma(a) = \max(a,0)$ in every layer.
    \item[$(ii)$] \textit{ICNN (Leaky ReLU).} Identical to $(i)$ but with the leaky-ReLU activation $\sigma(x) = \max(x,\alpha x)$, where $\alpha = 0.2$ is the negative slope.
    \item[$(iii)$] \textit{ICNNq (ReLU).} An ICNN whose first hidden layer is augmented by a learned quadratic skip connection:
    \begin{equation*}
        \bz_1 = \sigma\big(W_0 \bx + (W_{\textup{q}} \bx)^{\odot 2} + \bb_0\big),
    \end{equation*}
    where $W_{\textup{q}} \in \RR^{d_1 \times d}$ is a learned weight matrix, $(\,\cdot\,)^{\odot 2}$ denotes elementwise squaring, and $\sigma$ is the ReLU activation; all subsequent layers are defined as in the standard ICNN. The quadratic term injects a non-negative, input-convex contribution into the first layer and improves the ability of ICNNs to represent mildly curved potentials.
    \item[$(iv)$] \textit{ICNNq (Softplus).} Identical to $(iii)$ but with the activation replaced by the smooth Softplus $\sigma_\tau(a) = \tau \log(1 + e^{a/\tau})$ with temperature $\tau > 0$, which recovers ReLU as $\tau \to 0$. We consider parmeter choices $\tau \in \{0.1, 1, 10\}$ and report the results for all three values.
\end{enumerate}

The potential $f_{\theta_f}$ and the critic $g_{\theta_g}$ of each ICNN baseline are both instantiated as ICNNs of the same variant $(i)$--$(iv)$, width, and depth, but they are treated differently regarding the non-negativity of their hidden-to-hidden weight matrices $V_\ell$. We enforce  the potential $f_{\theta_f}$ to be input-convex by utilizing for $V_\ell \geq 0$  the same softplus reparametrization used for the HyCNN: each $V_\ell$ is represented as the entrywise softplus $V_\ell = \operatorname{softplus}(R_\ell) = \log(1 + \exp(R_\ell))$ of an unconstrained parameter tensor $R_\ell$, so that $V_\ell \in (0,\infty)^{n_{\ell+1}\times n_\ell}$ holds automatically on every forward pass and Adam can update $R_\ell$ in $\RR^{n_{\ell+1}\times n_\ell}$ without any projection. For the critic $g_{\theta_g}$, by contrast, strict input-convexity is not needed: $g_{\theta_g}$ enters the saddle problem only through the gradient $\nabla g_{\theta_g}(\bY)$ at target samples, and a mild soft convexity suffices to make the inner Legendre-type problem well-posed. We therefore drop the softplus reparametrization for $g_{\theta_g}$ and let each hidden-to-hidden matrix of $g_{\theta_g}$ be an ordinary unconstrained real parameter, with non-negativity merely encouraged softly through the convexity penalty $\lambda_{\textup{cvx}}\|(V_\ell)_{-}\|_F^2$ that appears in the training objective \eqref{eq:ICNN_objective} below.

At initialization, all $V_\ell$ are drawn so that their first and second moments match the values derived by \citet{hoedt2023principled} for ICNNs, namely
\begin{align*}
\mu_W = \sqrt{\tfrac{6\pi}{n_\ell\, D_\ell}}, \qquad \sigma_W^2 = \tfrac{1}{n_\ell}, \qquad D_\ell = 6(\pi-1) + (n_\ell-1)\big(3\sqrt{3} + 2\pi - 6\big),
\end{align*}
where $n_\ell$ is the fan-in of layer $\ell$. For the critic $g_{\theta_g}$, whose hidden-to-hidden matrices are unconstrained, we draw $(V_\ell)_{ij} \sim \calN(\mu_W,\sigma_W^2)$ directly. For the potential $f_{\theta_f}$, whose effective weight must be non-negative by construction, we instead draw $V_\ell$ entrywise from the log-normal distribution with the same prescribed moments, $(V_\ell)_{ij} \sim \operatorname{LogNormal}(\mu_{},\sigma_{}^2)$ with
\begin{align*}
 \mu_{} = \log\!\Big(\tfrac{\mu_W^2}{\sqrt{\mu_W^2 + \sigma_W^2}}\Big),\quad \sigma_{}^2 = \log\!\Big(1 + \tfrac{\sigma_W^2}{\mu_W^2}\Big), 
\end{align*}
and then store the corresponding pre-image $R_\ell = \operatorname{softplus}^{-1}(V_\ell) = \log(\exp(V_\ell) - 1)$. By construction the effective weight at initialization is always positive and satisfies $\EE[(V_\ell)_{ij}] = \mu_W$ and $\operatorname{Var}[(V_\ell)_{ij}] = \sigma_W^2$. We choose the log-normal distribution (rather than a truncated Gaussian) because it is inherently non-negative and allows us to match the prescribed mean and variance of \citet{hoedt2023principled} simultaneously.

The remaining parameters are identical for $f_{\theta_f}$ and $g_{\theta_g}$: the input-to-hidden matrices $W_\ell$ are unconstrained and initialized entrywise as $(W_\ell)_{ij}\sim\calN(0, 1/n_\ell)$ (LeCun-normal), the hidden-layer biases are set to the constant $\mu_b = -\sqrt{3n_\ell/D_\ell}$ and the output bias to zero, and for the two quadratic-skip variants $(iii)$--$(iv)$ the additional first-layer matrix $W_{\textup{q}} \in \RR^{n_1\times d}$ is drawn entrywise as $\calN(0, 1/d)$. All random matrices are drawn independently across layers.
%

All ICNN-based methods are trained by solving an empirical saddle-point problem similar to our HyCNN-based estimator, with the HyCNN potential and critic replaced by the respective ICNN variant and an additional regularization term. We refer to the resulting objective as the ICNN objective; for mini-batches $(\bX_i)_{i\in [M]}$ and $(\bY_j)_{j\in [M]}$ of size $M$, it takes the form
\begin{align}\label{eq:ICNN_objective}
  \min_{\theta_f}\;\max_{\theta_g}\; \bigg\{ \textstyle\frac{1}{M}\sum_{i=1}^{M} \!\Big[ f_{\theta_f}(\bX_i) + \langle \bY_i, \nabla g_{\theta_g}(\bY_i) \rangle - f_{\theta_f}(\nabla g_{\theta_g}(\bY_i))\Big] \;-\; \lambda_{\textup{cvx}}\, \textstyle\sum_{V \in \theta_g} \| (V)_{-} \|_F^2 \bigg\},
\end{align}
where $(V)_{-} \coloneqq \max(0, -V)$ denotes the negative part of $V$ taken elementwise, $\|\cdot\|_F$ is the Frobenius norm, and the sum ranges over all hidden-to-hidden weight matrices $V$ of the critic network $g_{\theta_g}$. The parameter $\lambda_{\textup{cvx}} > 0$ controls the strength of the convexity regularization and softly penalizes negative entries in the hidden-to-hidden weights of the critic but does not enforce strict non-negativity. We use the same value $\lambda_{\textup{cvx}} = 1$ for all ICNN-based methods. The potential $f_{\theta_f}$ and the critic $g_{\theta_g}$ are parameterized by the same architecture (width, depth, activation).

For training we follow the same alternating optimization scheme as for the HyCNN-based estimator, which is inspired by \citet[Algorithm~1]{makkuva2020optimal}. We run $T = 1000$ outer iterations with $S = 5$ inner steps, batch size $M = 256$, and the Adam optimizer \citep{kingma2014adam} with $\beta_1 = 0.5$, $\beta_2 = 0.9$, initial learning rate $\lambda = 10^{-2}$, and cosine decay to final ratio $0.01$, applied identically to both $\theta_f$ and $\theta_g$. The OT map estimate is then read off as $\hat T = \nabla f_{\theta_f}$.

%
%
%
%
%
%
%
%
%

\parabold{Monge Gap estimator}
As a further baseline that does not rely on input-convex parameterizations, we include the Monge Gap estimator of \citet{uscidda2023monge}. Here the OT map is parameterized directly as a plain MLP $T_\theta\colon \RR^d \to \RR^d$ with ELU activations (following the original implementation) and hidden widths $(64,\dots,64)$ of depth $L \in \{2, 4, 6\}$ (matching the ICNN baselines). For source and target mini-batches $\bX_1,\dots,\bX_M$ and $\bY_1,\dots,\bY_M$ of size $M$, let $\hat P_M = \tfrac{1}{M}\sum_i \delta_{\bX_i}$, $\hat Q_M = \tfrac{1}{M}\sum_i \delta_{\bY_i}$ and $(T_\theta)_\# \hat P_M = \tfrac{1}{M}\sum_i \delta_{T_\theta(\bX_i)}$ denote the associated empirical measures. Upon writing $c(\bx,\by) = \tfrac{1}{2}\|\bx-\by\|_2^2$ for the squared-Euclidean cost and
\begin{align*}
\mathrm{OT}_\varepsilon(\mu,\nu) \;\coloneqq\; \min_{\pi \in \Pi(\mu,\nu)} \int c\, \mathrm{d}\pi + \varepsilon\, \mathrm{KL}(\pi \,\|\, \mu \otimes \nu)
\end{align*}
for the entropic OT cost, the training objective combines a Sinkhorn fitting loss and the entropic Monge gap of \citet{uscidda2023monge}, namely
\begin{align}\label{eq:monge_gap_objective}
\min_\theta \; \underbrace{\calS_\varepsilon\big((T_\theta)_\# \hat P_M,\, \hat Q_M\big)}_{\text{fitting loss}} \;+\; \lambda\, \underbrace{\Big[\, \textstyle\frac{1}{M}\sum_{i=1}^M c\big(\bX_i, T_\theta(\bX_i)\big) \;-\; \mathrm{OT}_\varepsilon\!\big(\hat P_M, (T_\theta)_\# \hat P_M\big)\Big]}_{\text{Monge gap }\mathcal{M}_\varepsilon(T_\theta;\, \hat P_M)},
\end{align}
where $\calS_\varepsilon(\mu,\nu) = \mathrm{OT}_\varepsilon(\mu,\nu) - \tfrac{1}{2}\mathrm{OT}_\varepsilon(\mu,\mu) - \tfrac{1}{2}\mathrm{OT}_\varepsilon(\nu,\nu)$ denotes the (debiased) Sinkhorn divergence with squared-Euclidean costs. The gap $\mathcal{M}_\varepsilon(T_\theta;\hat P_M)\geq 0$ vanishes whenever $T_\theta$ transports $\hat P_M$ to $(T_\theta)_\# \hat P_M$ at near OT cost, i.e., whenever $T_\theta$ is itself nearly the gradient of a convex function. Both terms in \eqref{eq:monge_gap_objective} are evaluated via differentiable Sinkhorn iterations provided by the \texttt{ott-jax} library of \citet{cuturi2022optimal}. We set the entropic regularization to $\varepsilon = 0.05$, the Monge-gap weight to $\lambda = 0.1$, and use mean cost normalization (i.e., normalizing the cost function along the training samples to ensure that the average cost equals one) following the default configuration in \citet{uscidda2023monge}. Training minimizes \eqref{eq:monge_gap_objective} by Adam with fixed learning rate $10^{-2}$ as the objective involves no saddle point problem, batch size $M = 256$, and $T = 1000$ outer iterations; all remaining hyperparameters are kept at their \texttt{ott-jax} defaults.

\parabold{Prediction MSE tables for OT map estimation}\label{sec:OT_testmse_tables}

We first present the prediction MSE of the estimated OT map $\hat T = \nabla \hat \phi$ against the ground-truth OT map $\overline T = \nabla \phi_\ell$ for each of the four OT potentials (a)--(d) and dimensions $d \in \{10, 20, 50\}$. The MSE is evaluated on an independent test set of $N_{\text{test}} = 1{,}000$ samples; mean and standard error (SE) are computed over $10$ independent runs. We compare a comprehensive set of estimators: ICNN with ReLU and Leaky ReLU activations, ICNNq with a quadratic skip connection and either ReLU or Softplus activations (the latter for varying smoothness parameters $\tau \in \{0.1, 1, 10\}$), HyCNN with the log-sum-exp activation for $\tau \in \{0.1, 1, 10\}$, the Monge Gap estimator, and entropic OT (EOT) with entropy regularization parameter $\epsilon \in \{0.1, 1, 10\}$. We only report the results for the HyCNN architecture (depth $L$ and smoothness $\tau$) that achieves the smallest Sinkhorn divergence an independent validation set as described in the next section, and we report the results for all $\tau$ variants of ICNNs to provide a comprehensive picture of the performance of these baselines across different smoothness levels.
%
All ICNN architectures use width $64$ whereas HyCNNs use width $48$, with depths $L \in \{2, 4, 6\}$. The full training setup is described above.
 
The results in Tables \ref{tab:ot_testmse_collapsed_psi1}, \ref{tab:ot_testmse_collapsed_psi4}, \ref{tab:ot_testmse_collapsed_psi2}, and \ref{tab:ot_testmse_collapsed_psi3} reveal several consistent patterns. On the smooth quadratic targets (a) and (b), HyCNN is the best estimator in every dimension and the three HyCNN architectures form the three smallest MSE entries throughout, dominating all baselines, including the strongest ICNN-based competitor, ICNNq (Softplus), by a factor of roughly $3$--$5$ in MSE. Here the large smoothness setting $\tau = 10$ is uniformly preferred by the Sinkhorn validation criterion. On the non-smooth target (c), HyCNN remains best at $d \in \{20, 50\}$ and is only marginally surpassed by the tuned ICNNq (Softplus) configuration at $d = 10$. On the strongly curved target (d), by contrast, ICNNq (Softplus) with a small to moderate temperature $\tau \in \{0.1, 1\}$ clearly beats HyCNN at $d = 10$ and $d = 20$, whereas HyCNN regains the lead at $d = 50$. For HyCNN on (c) and (d) the optimal smoothness is target- and dimension-dependent, with small $\tau \in \{0.1, 1\}$ preferred at $d = 10$ and $\tau = 10$ most accurate and stable at $d = 50$. Among the ICNN baselines, the quadratic-skip variants (ICNNq) clearly outperform the plain ICNN variants across all settings, and the Softplus activation is consistently more accurate and more stable than ReLU once $\tau$ is tuned: small $\tau \in \{0.1, 1\}$ is preferred at $d \in \{10, 20\}$, while large $\tau = 10$ is required at $d = 50$ to avoid the depth-induced instabilities exhibited by ICNNq (ReLU) at $L \in \{4, 6\}$ on targets (c) and (d). Even ICNNq (Softplus) with small $\tau = 0.1$ degrades sharply at $L = 6$, $d = 50$ on the non-smooth and strongly curved targets, confirming that low smoothness amplifies high-dimensional instabilities. ICNN (L-ReLU) is the least robust method overall and exhibits catastrophic failures at $L = 2$, $d = 50$ across all four targets. The best entropic OT estimator is uniformly worst on (a)--(d), and the Monge Gap is outperformed by HyCNN by an order of magnitude in nearly all settings. HyCNN remains stable across $L \in \{2, 4, 6\}$ once $\tau$ is chosen appropriately, with its relative advantage most pronounced on the smooth quadratic targets and at high dimensions.

\parabold{Sinkhorn divergence tables for HyCNN architecture selection}\label{sec:OT_sinkhorn_tables}

In addition to the prediction MSE tables above, we present Sinkhorn divergence tables (with regularization $\varepsilon = 0.1$) evaluated on an independent validation set of $n_{\text{valid}} = 1{,}000$ fresh sample pairs from $P$ and $Q = (\nabla \phi_\ell)_\# P$, computed separately from the training and test data. This validation metric assesses the distributional fit of the learned OT map and serves as a guide for selecting the HyCNN architecture (depth $L$ and smoothness parameter $\tau$) for a given problem. Concretely, for a HyCNN estimator $\hat T$ based on training data, we compute for empirical measures $\hat P_{n_{\text{valid}}}, \hat Q_{n_{\text{valid}}}$ the Sinkhorn divergence \citep{feydy2019interpolating, peyre2019computational} based on the squared Euclidean distance with regularization parameter $\epsilon = 0.1$, 
\begin{align*}
    \mathcal{S}_{\epsilon}(\hat T_{\#} \hat P_{n_{\text{valid}}}, \hat Q_{n_{\text{valid}}}).
\end{align*}
For each simulation run, we draw a single pair of validation data sets from domain and target and compute the above Sinkhorn divergence. Given the $10$ independent runs for training, we thus compute $10$ independent Sinkhorn divergence values which we use to compute mean and standard error (SE). The resulting validation metrics for the HyCNN based OT estimators are depicted in Tables \ref{tab:ot_sinkhorn_full_psi1},
\ref{tab:ot_sinkhorn_full_psi4},
\ref{tab:ot_sinkhorn_full_psi2}, and \ref{tab:ot_sinkhorn_full_psi3},   right below the respective prediction MSE table with the same ground truth. 

%
The Sinkhorn divergence validation metrics demonstrate that a well-performing HyCNN estimator can be consistently identified through our validation procedure. We conducted analogous experiments with alternative choices of the regularization parameter $\epsilon$ and found the validation technique to yield consistent results across these settings. A noteworthy observation is that identifying an estimator with even a moderately smaller Sinkhorn divergence can translate into a significantly improved fit. We find this phenomenon striking and attribute it to high-dimensional effects as it is inherently difficult to certify a substantially better distributional fit on the basis of independent realizations alone. %

%

%
\begin{table}[h!]
\caption{Prediction MSE (mean and SE over $10$ runs) of the estimated OT map for the OT map (a) $\textstyle T_1(\bx) = \bx$ based on $n = m = 5000$ independent training sample points from the source and target distribution. Per HyCNN architecture ($48 \times L$), the $\tau$ variant with the smallest Sinkhorn divergence validation metric ($\epsilon = 0.1$) for $1000$ independent validation samples at that dimension is used; see Table~\ref{tab:ot_sinkhorn_full_psi1}. Per dimension, the smallest mean MSE per method type is bold and colored, with the \underline{three smallest} values across all methods underlined.}
\label{tab:ot_testmse_collapsed_psi1}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{Method $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
\multirow{3}{*}{Entropic OT} & $\epsilon = 0.1$ & 2.678 (0.017) & 12.098 (0.039) & 51.783 (0.075) \\
 & $\epsilon = 1$ & \textcolor[HTML]{006400}{\textbf{0.999}} (0.008) & \textcolor[HTML]{006400}{\textbf{6.537}} (0.034) & 41.019 (0.067) \\
 & $\epsilon = 10$ & 6.538 (0.022) & 13.129 (0.031) & \textcolor[HTML]{006400}{\textbf{32.786}} (0.058) \\
\midrule
\multirow{3}{*}{MongeGap} & $(64 \times 2)$ & \textcolor[HTML]{E334D4}{\textbf{1.067}} (0.016) & \textcolor[HTML]{E334D4}{\textbf{4.532}} (0.042) & 22.429 (0.150) \\
 & $(64 \times 4)$ & 1.210 (0.035) & 5.296 (0.091) & 21.936 (0.106) \\
 & $(64 \times 6)$ & 1.217 (0.048) & 5.301 (0.117) & \textcolor[HTML]{E334D4}{\textbf{19.610}} (0.109) \\
\midrule
\multirow{3}{*}{ICNN (ReLU)} & $(64 \times 2)$ & 0.852 (0.021) & 3.221 (0.061) & 20.792 (0.567) \\
 & $(64 \times 4)$ & 0.498 (0.010) & 2.222 (0.038) & 12.205 (0.352) \\
 & $(64 \times 6)$ & \textcolor[HTML]{F3A11C}{\textbf{0.391}} (0.007) & \textcolor[HTML]{F3A11C}{\textbf{1.965}} (0.065) & \textcolor[HTML]{F3A11C}{\textbf{9.809}} (0.186) \\
\midrule
\multirow{3}{*}{ICNN (L-ReLU)} & $(64 \times 2)$ & 1.213 (0.055) & 4.360 (0.135) & 614.316 (216.829) \\
 & $(64 \times 4)$ & 0.734 (0.029) & 2.599 (0.089) & 20.861 (1.983) \\
 & $(64 \times 6)$ & \textcolor[HTML]{A46500}{\textbf{0.679}} (0.130) & \textcolor[HTML]{A46500}{\textbf{2.002}} (0.072) & \textcolor[HTML]{A46500}{\textbf{10.183}} (0.474) \\
\midrule
\multirow{3}{*}{ICNNq (ReLU)} & $(64 \times 2)$ & \textcolor[HTML]{E56B00}{\textbf{0.222}} (0.009) & \textcolor[HTML]{E56B00}{\textbf{0.801}} (0.067) & \textcolor[HTML]{E56B00}{\textbf{4.101}} (0.299) \\
 & $(64 \times 4)$ & 0.286 (0.011) & 1.123 (0.062) & 9.581 (0.479) \\
 & $(64 \times 6)$ & 3.788 (3.404) & 1.401 (0.049) & 127.802 (79.678) \\
\midrule
\multirow{9}{*}{ICNNq (Softplus)} & $(64 \times 2)$; $\tau = 0.1$ & 0.121 (0.008) & 0.567 (0.031) & 3.350 (0.143) \\
 & $(64 \times 2)$; $\tau = 1$ & \textcolor[HTML]{8B1301}{\textbf{0.073}} (0.002) & \textcolor[HTML]{8B1301}{\textbf{0.365}} (0.020) & 3.032 (0.256) \\
 & $(64 \times 2)$; $\tau = 10$ & 0.195 (0.007) & 0.486 (0.010) & \textcolor[HTML]{8B1301}{\textbf{2.046}} (0.028) \\
 & $(64 \times 4)$; $\tau = 0.1$ & 0.192 (0.004) & 0.858 (0.036) & 7.563 (0.283) \\
 & $(64 \times 4)$; $\tau = 1$ & 0.103 (0.003) & 0.407 (0.017) & 6.950 (0.244) \\
 & $(64 \times 4)$; $\tau = 10$ & 0.188 (0.008) & 0.490 (0.007) & 2.367 (0.020) \\
 & $(64 \times 6)$; $\tau = 0.1$ & 0.233 (0.010) & 0.971 (0.010) & 10.011 (1.030) \\
 & $(64 \times 6)$; $\tau = 1$ & 0.097 (0.003) & 0.570 (0.050) & 6.617 (1.388) \\
 & $(64 \times 6)$; $\tau = 10$ & 0.186 (0.007) & 0.504 (0.005) & 2.482 (0.021) \\
\midrule
\multirow{3}{*}{HyCNN} & $(48 \times 2)$ & \underline{0.027} (0.001) & \underline{0.109} (0.005) & \underline{0.719} (0.013) \\
 & $(48 \times 4)$ & \textcolor[HTML]{0080DB}{\underline{\textbf{0.023}}} (0.001) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.067}}} (0.002) & \underline{0.392} (0.006) \\
 & $(48 \times 6)$ & \underline{0.065} (0.001) & \underline{0.076} (0.003) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.386}}} (0.004) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
\begin{table}[h!]
\caption{Sinkhorn divergence (mean and SE over $10$ runs) of the estimated OT map for the OT map (a) $\textstyle T_1(\bx) = \bx$. Per HyCNN architecture ($48 \times L$) and per dimension, the $\tau$ variant with the smallest mean Sinkhorn divergence is bold and colored, with the \underline{three smallest} values across all HyCNN rows underlined.}
\label{tab:ot_sinkhorn_full_psi1}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{HyCNN architecture $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
 & $(48 \times 2)$; $\tau = 0.1$ & 4.309 (0.024) & 15.970 (0.051) & 61.780 (0.167) \\
 & $(48 \times 2)$; $\tau = 1$ & 4.112 (0.020) & 15.585 (0.048) & 60.994 (0.088) \\
 & $(48 \times 2)$; $\tau = 10$ & \textcolor[HTML]{0080DB}{\underline{\textbf{4.032}}} (0.020) & \underline{\textbf{14.900}} (0.034) & \underline{\textbf{57.793}} (0.102) \\ \hline
 & $(48 \times 4)$; $\tau = 0.1$ & 4.191 (0.027) & 15.600 (0.040) & 62.591 (0.109) \\
 & $(48 \times 4)$; $\tau = 1$ & 4.056 (0.019) & 15.343 (0.035) & 60.454 (0.155) \\
 & $(48 \times 4)$; $\tau = 10$ & \underline{\textbf{4.044}} (0.018) & \underline{\textbf{14.900}} (0.031) & \underline{\textbf{57.555}} (0.091) \\ \hline
 & $(48 \times 6)$; $\tau = 0.1$ & 4.228 (0.021) & 15.567 (0.031) & 61.553 (0.078) \\
 & $(48 \times 6)$; $\tau = 1$ & \underline{\textbf{4.047}} (0.019) & 15.065 (0.032) & 59.543 (0.115) \\
 & $(48 \times 6)$; $\tau = 10$ & 4.054 (0.021) & \textcolor[HTML]{0080DB}{\underline{\textbf{14.888}}} (0.026) & \textcolor[HTML]{0080DB}{\underline{\textbf{57.499}}} (0.096) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
\begin{table}[h!]
\caption{Prediction MSE (mean and SE over $10$ runs) of the estimated OT map for the OT map (b) $\textstyle T_2(\bx) = \bigl((1 + \frac{\sin(i)}{2})\, x_i\bigr)_{i\in [d]}$ based on $n = m = 5000$ independent training sample points from the source and target distribution. Per HyCNN architecture ($48 \times L$), the $\tau$ variant with the smallest Sinkhorn divergence validation metric ($\epsilon = 0.1$) for $1000$ independent validation samples at that dimension is used; see Table~\ref{tab:ot_sinkhorn_full_psi4}. Per dimension, the smallest mean MSE per method type is bold and colored, with the \underline{three smallest} values across all methods underlined.}
\label{tab:ot_testmse_collapsed_psi4}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{Method $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
\multirow{3}{*}{Entropic OT} & $\epsilon = 0.1$ & 2.927 (0.018) & 12.404 (0.033) & 52.669 (0.107) \\
 & $\epsilon = 1$ & \textcolor[HTML]{006400}{\textbf{1.078}} (0.011) & \textcolor[HTML]{006400}{\textbf{6.589}} (0.034) & 41.518 (0.101) \\
 & $\epsilon = 10$ & 7.435 (0.026) & 14.022 (0.040) & \textcolor[HTML]{006400}{\textbf{33.704}} (0.084) \\
\midrule
\multirow{3}{*}{MongeGap} & $(64 \times 2)$ & \textcolor[HTML]{E334D4}{\textbf{1.383}} (0.033) & 5.053 (0.037) & 20.856 (0.110) \\
 & $(64 \times 4)$ & 1.558 (0.053) & 5.149 (0.070) & 19.127 (0.140) \\
 & $(64 \times 6)$ & 1.617 (0.045) & \textcolor[HTML]{E334D4}{\textbf{4.994}} (0.075) & \textcolor[HTML]{E334D4}{\textbf{16.897}} (0.088) \\
\midrule
\multirow{3}{*}{ICNN (ReLU)} & $(64 \times 2)$ & 1.010 (0.010) & 3.822 (0.058) & 19.617 (0.202) \\
 & $(64 \times 4)$ & 0.597 (0.007) & 2.341 (0.064) & 12.451 (0.180) \\
 & $(64 \times 6)$ & \textcolor[HTML]{F3A11C}{\textbf{0.426}} (0.007) & \textcolor[HTML]{F3A11C}{\textbf{1.939}} (0.066) & \textcolor[HTML]{F3A11C}{\textbf{9.786}} (0.248) \\
\midrule
\multirow{3}{*}{ICNN (L-ReLU)} & $(64 \times 2)$ & 1.389 (0.071) & 4.702 (0.157) & 60.328 (17.675) \\
 & $(64 \times 4)$ & 0.779 (0.031) & 2.735 (0.153) & 16.110 (0.854) \\
 & $(64 \times 6)$ & \textcolor[HTML]{A46500}{\textbf{0.541}} (0.021) & \textcolor[HTML]{A46500}{\textbf{2.161}} (0.068) & \textcolor[HTML]{A46500}{\textbf{9.996}} (0.275) \\
\midrule
\multirow{3}{*}{ICNNq (ReLU)} & $(64 \times 2)$ & \textcolor[HTML]{E56B00}{\textbf{0.249}} (0.020) & \textcolor[HTML]{E56B00}{\textbf{0.694}} (0.046) & \textcolor[HTML]{E56B00}{\textbf{3.633}} (0.241) \\
 & $(64 \times 4)$ & 0.318 (0.029) & 1.059 (0.037) & 8.347 (0.260) \\
 & $(64 \times 6)$ & 0.368 (0.018) & 1.455 (0.060) & 26.901 (9.868) \\
\midrule
\multirow{9}{*}{ICNNq (Softplus)} & $(64 \times 2)$; $\tau = 0.1$ & 0.139 (0.008) & 0.550 (0.023) & 3.259 (0.174) \\
 & $(64 \times 2)$; $\tau = 1$ & \textcolor[HTML]{8B1301}{\textbf{0.078}} (0.003) & \textcolor[HTML]{8B1301}{\textbf{0.324}} (0.012) & 3.447 (0.257) \\
 & $(64 \times 2)$; $\tau = 10$ & 0.242 (0.013) & 0.570 (0.006) & \textcolor[HTML]{8B1301}{\textbf{2.019}} (0.056) \\
 & $(64 \times 4)$; $\tau = 0.1$ & 0.215 (0.008) & 0.833 (0.031) & 7.303 (0.289) \\
 & $(64 \times 4)$; $\tau = 1$ & 0.108 (0.003) & 0.445 (0.037) & 6.358 (0.318) \\
 & $(64 \times 4)$; $\tau = 10$ & 0.242 (0.007) & 0.553 (0.011) & 2.419 (0.034) \\
 & $(64 \times 6)$; $\tau = 0.1$ & 0.251 (0.012) & 1.022 (0.019) & 20.532 (12.168) \\
 & $(64 \times 6)$; $\tau = 1$ & 0.111 (0.003) & 0.603 (0.028) & 4.063 (0.280) \\
 & $(64 \times 6)$; $\tau = 10$ & 0.243 (0.009) & 0.584 (0.015) & 2.472 (0.024) \\
\midrule
\multirow{3}{*}{HyCNN} & $(48 \times 2)$ & \underline{0.030} (0.001) & \underline{0.102} (0.003) & \underline{0.676} (0.020) \\
 & $(48 \times 4)$ & \textcolor[HTML]{0080DB}{\underline{\textbf{0.029}}} (0.003) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.071}}} (0.002) & \textcolor[HTML]{0080DB}{\underline{\textbf{0.406}}} (0.005) \\
 & $(48 \times 6)$ & \underline{0.073} (0.004) & \underline{0.106} (0.004) & \underline{0.499} (0.018) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
\begin{table}[h!]
\caption{
Sinkhorn divergence (mean and SE over $10$ runs) of the estimated OT map for the OT map (b) $\textstyle T_2(\bx) = \bigl((1 + \frac{\sin(i)}{2})\, x_i\bigr)_{i\in [d]}$. Per HyCNN architecture ($48 \times L$) and per dimension, the $\tau$ variant with the smallest mean Sinkhorn divergence is bold and colored, with the \underline{three smallest} values across all HyCNN rows underlined.}
\label{tab:ot_sinkhorn_full_psi4}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{HyCNN architecture $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
 & $(48 \times 2)$; $\tau = 0.1$ & 4.542 (0.035) & 16.132 (0.084) & 62.161 (0.336) \\
 & $(48 \times 2)$; $\tau = 1$ & 4.337 (0.028) & 15.596 (0.043) & 61.467 (0.080) \\
 & $(48 \times 2)$; $\tau = 10$ & \textcolor[HTML]{0080DB}{\underline{\textbf{4.261}}} (0.025) & \textcolor[HTML]{0080DB}{\underline{\textbf{14.897}}} (0.035) & \underline{\textbf{58.242}} (0.111) \\ \hline
 & $(48 \times 4)$; $\tau = 0.1$ & 4.439 (0.033) & 15.650 (0.046) & 63.229 (0.147) \\
 & $(48 \times 4)$; $\tau = 1$ & 4.281 (0.025) & 15.302 (0.043) & 60.680 (0.238) \\
 & $(48 \times 4)$; $\tau = 10$ & \textbf{4.277} (0.025) & \underline{\textbf{14.913}} (0.036) & \textcolor[HTML]{0080DB}{\underline{\textbf{58.124}}} (0.115) \\ \hline
 & $(48 \times 6)$; $\tau = 0.1$ & 4.468 (0.026) & 15.621 (0.045) & 61.882 (0.142) \\
 & $(48 \times 6)$; $\tau = 1$ & \underline{\textbf{4.267}} (0.026) & 15.044 (0.037) & 59.665 (0.155) \\
 & $(48 \times 6)$; $\tau = 10$ & \underline{4.274} (0.026) & \underline{\textbf{14.936}} (0.040) & \underline{\textbf{58.450}} (0.130) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
\begin{table}[h!]
\caption{Prediction MSE (mean and SE over $10$ runs) of the estimated OT map for the OT map (c) $\textstyle T_3(\bx) = (x_i + \textup{sign}(x_i))_{i\in [d]}$ based on $n = m = 5000$ independent training sample points from the source and target distribution. Per HyCNN architecture ($48 \times L$), the $\tau$ variant with the smallest Sinkhorn divergence validation metric ($\epsilon = 0.1$) for $1000$ independent validation samples at that dimension is used; see Table~\ref{tab:ot_sinkhorn_full_psi2}. Per dimension, the smallest mean MSE per method type is bold and colored, with the \underline{three smallest} values across all methods underlined.}
\label{tab:ot_testmse_collapsed_psi2}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{Method $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
\multirow{3}{*}{Entropic OT} & $\epsilon = 0.1$ & 8.155 (0.033) & 42.243 (0.072) & 189.406 (0.327) \\
 & $\epsilon = 1$ & \textcolor[HTML]{006400}{\textbf{3.834}} (0.024) & \textcolor[HTML]{006400}{\textbf{30.997}} (0.111) & 169.342 (0.385) \\
 & $\epsilon = 10$ & 16.868 (0.025) & 33.891 (0.029) & \textcolor[HTML]{006400}{\textbf{89.193}} (0.108) \\
\midrule
\multirow{3}{*}{MongeGap} & $(64 \times 2)$ & \textcolor[HTML]{E334D4}{\textbf{5.371}} (0.060) & \textcolor[HTML]{E334D4}{\textbf{19.623}} (0.067) & 84.647 (0.283) \\
 & $(64 \times 4)$ & 7.208 (0.142) & 19.640 (0.041) & 75.989 (0.205) \\
 & $(64 \times 6)$ & 7.476 (0.107) & 19.933 (0.111) & \textcolor[HTML]{E334D4}{\textbf{65.164}} (0.212) \\
\midrule
\multirow{3}{*}{ICNN (ReLU)} & $(64 \times 2)$ & 4.670 (0.263) & 20.552 (0.149) & 89.585 (1.698) \\
 & $(64 \times 4)$ & \textcolor[HTML]{F3A11C}{\textbf{2.165}} (0.133) & 13.822 (0.240) & 66.244 (2.288) \\
 & $(64 \times 6)$ & 2.461 (0.209) & \textcolor[HTML]{F3A11C}{\textbf{9.641}} (0.673) & \textcolor[HTML]{F3A11C}{\textbf{55.948}} (0.771) \\
\midrule
\multirow{3}{*}{ICNN (L-ReLU)} & $(64 \times 2)$ & 134.056 (115.902) & $2.29 \cdot 10^{3}$ (1572.207) & $3.82 \cdot 10^{3}$ (1134.576) \\
 & $(64 \times 4)$ & 2.784 (0.196) & 13.704 (0.131) & 85.385 (2.898) \\
 & $(64 \times 6)$ & \textcolor[HTML]{A46500}{\textbf{2.271}} (0.194) & \textcolor[HTML]{A46500}{\textbf{11.384}} (0.232) & \textcolor[HTML]{A46500}{\textbf{59.944}} (2.004) \\
\midrule
\multirow{3}{*}{ICNNq (ReLU)} & $(64 \times 2)$ & 1.522 (0.067) & 8.499 (0.057) & \textcolor[HTML]{E56B00}{\textbf{26.985}} (0.571) \\
 & $(64 \times 4)$ & \textcolor[HTML]{E56B00}{\textbf{1.220}} (0.026) & 7.211 (0.350) & 48.320 (1.869) \\
 & $(64 \times 6)$ & 1.558 (0.093) & \textcolor[HTML]{E56B00}{\textbf{5.828}} (0.387) & 61.714 (0.967) \\
\midrule
\multirow{9}{*}{ICNNq (Softplus)} & $(64 \times 2)$; $\tau = 0.1$ & 1.605 (0.165) & 8.410 (0.055) & 28.272 (1.198) \\
 & $(64 \times 2)$; $\tau = 1$ & 3.519 (0.035) & 8.172 (0.025) & \textcolor[HTML]{8B1301}{\textbf{24.779}} (0.495) \\
 & $(64 \times 2)$; $\tau = 10$ & 4.769 (0.036) & 9.492 (0.040) & 25.550 (0.229) \\
 & $(64 \times 4)$; $\tau = 0.1$ & \textcolor[HTML]{8B1301}{\underline{\textbf{0.942}}} (0.021) & 6.896 (0.494) & 44.097 (2.595) \\
 & $(64 \times 4)$; $\tau = 1$ & 3.231 (0.071) & 8.967 (0.105) & 30.605 (0.596) \\
 & $(64 \times 4)$; $\tau = 10$ & 4.620 (0.047) & 9.634 (0.068) & 27.468 (0.149) \\
 & $(64 \times 6)$; $\tau = 0.1$ & 1.069 (0.018) & \textcolor[HTML]{8B1301}{\underline{\textbf{5.025}}} (0.480) & 228.345 (118.208) \\
 & $(64 \times 6)$; $\tau = 1$ & 2.878 (0.081) & 9.241 (0.102) & 28.474 (0.415) \\
 & $(64 \times 6)$; $\tau = 10$ & 4.565 (0.047) & 9.568 (0.056) & 27.948 (0.100) \\
\midrule
\multirow{3}{*}{HyCNN} & $(48 \times 2)$ & 1.873 (0.042) & 7.716 (0.026) & \underline{21.572} (0.077) \\
 & $(48 \times 4)$ & \underline{1.026} (0.010) & \textcolor[HTML]{0080DB}{\underline{\textbf{4.704}}} (0.248) & \underline{19.840} (0.038) \\
 & $(48 \times 6)$ & \textcolor[HTML]{0080DB}{\underline{\textbf{1.009}}} (0.016) & \underline{5.571} (0.168) & \textcolor[HTML]{0080DB}{\underline{\textbf{19.771}}} (0.053) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
\begin{table}[h!]
\caption{Sinkhorn divergence (mean and SE over $10$ runs) of the estimated OT map for the OT map (c) $\textstyle T_3(\bx) = (x_i + \textup{sign}(x_i))_{i\in [d]}$. Per HyCNN architecture ($48 \times L$) and per dimension, the $\tau$ variant with the smallest mean Sinkhorn divergence is bold and colored, with the \underline{three smallest} values across all HyCNN rows underlined.}
\label{tab:ot_sinkhorn_full_psi2}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{HyCNN architecture $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
 & $(48 \times 2)$; $\tau = 0.1$ & \underline{\textbf{10.721}} (0.077) & 54.105 (0.292) & 221.403 (0.919) \\
 & $(48 \times 2)$; $\tau = 1$ & 11.884 (0.126) & 54.741 (0.187) & 209.904 (0.644) \\
 & $(48 \times 2)$; $\tau = 10$ & 14.601 (0.076) & \textbf{53.160} (0.070) & \underline{\textbf{206.881}} (0.311) \\ \hline
 & $(48 \times 4)$; $\tau = 0.1$ & \underline{\textbf{10.576}} (0.082) & \underline{50.521} (0.125) & 219.477 (0.501) \\
 & $(48 \times 4)$; $\tau = 1$ & 11.161 (0.077) & \textcolor[HTML]{0080DB}{\underline{\textbf{48.541}}} (0.376) & 210.959 (0.286) \\
 & $(48 \times 4)$; $\tau = 10$ & 14.668 (0.083) & 53.117 (0.073) & \underline{\textbf{206.099}} (0.296) \\ \hline
 & $(48 \times 6)$; $\tau = 0.1$ & \textcolor[HTML]{0080DB}{\underline{\textbf{10.570}}} (0.076) & \underline{\textbf{50.527}} (0.144) & 214.874 (0.444) \\
 & $(48 \times 6)$; $\tau = 1$ & 11.498 (0.098) & 50.545 (0.277) & 208.679 (0.276) \\
 & $(48 \times 6)$; $\tau = 10$ & 14.647 (0.075) & 53.056 (0.056) & \textcolor[HTML]{0080DB}{\underline{\textbf{205.461}}} (0.309) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
\begin{table}[h!]
\caption{Prediction MSE (mean and SE over $10$ runs) of the estimated OT map for the OT map (d) $\textstyle T_4(\bx) = (4x_i^3)_{i \in [d]}$ based on $n = m = 5000$ independent training sample points from the source and target distribution. Per HyCNN architecture ($48 \times L$), the $\tau$ variant with the smallest Sinkhorn divergence validation metric ($\epsilon = 0.1$) for $1000$ independent validation samples at that dimension is used; see Table~\ref{tab:ot_sinkhorn_full_psi3}. Per dimension, the smallest mean MSE per method type is bold and colored, with the \underline{three smallest} values across all methods underlined.}
\label{tab:ot_testmse_collapsed_psi3}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{Method $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
\multirow{3}{*}{Entropic OT} & $\epsilon = 0.1$ & 8.990 (0.046) & 32.534 (0.144) & 128.256 (0.323) \\
 & $\epsilon = 1$ & \textcolor[HTML]{006400}{\textbf{3.417}} (0.029) & \textcolor[HTML]{006400}{\textbf{16.729}} (0.092) & 98.421 (0.422) \\
 & $\epsilon = 10$ & 16.439 (0.073) & 32.839 (0.138) & \textcolor[HTML]{006400}{\textbf{82.155}} (0.217) \\
\midrule
\multirow{3}{*}{MongeGap} & $(64 \times 2)$ & 10.756 (0.186) & 19.018 (0.242) & 55.945 (0.267) \\
 & $(64 \times 4)$ & \textcolor[HTML]{E334D4}{\textbf{10.500}} (0.179) & \textcolor[HTML]{E334D4}{\textbf{18.823}} (0.178) & 52.765 (0.218) \\
 & $(64 \times 6)$ & 11.182 (0.242) & 19.123 (0.166) & \textcolor[HTML]{E334D4}{\textbf{51.618}} (0.163) \\
\midrule
\multirow{3}{*}{ICNN (ReLU)} & $(64 \times 2)$ & 5.675 (0.143) & 14.824 (0.200) & 68.621 (2.424) \\
 & $(64 \times 4)$ & 4.821 (0.081) & 13.891 (0.320) & 46.814 (0.934) \\
 & $(64 \times 6)$ & \textcolor[HTML]{F3A11C}{\textbf{3.909}} (0.080) & \textcolor[HTML]{F3A11C}{\textbf{11.780}} (0.297) & \textcolor[HTML]{F3A11C}{\textbf{41.207}} (0.559) \\
\midrule
\multirow{3}{*}{ICNN (L-ReLU)} & $(64 \times 2)$ & 6.677 (0.120) & 21.465 (0.546) & $4.5 \cdot 10^{3}$ (2303.743) \\
 & $(64 \times 4)$ & 5.140 (0.131) & 13.069 (0.265) & 65.749 (1.899) \\
 & $(64 \times 6)$ & \textcolor[HTML]{A46500}{\textbf{4.823}} (0.163) & \textcolor[HTML]{A46500}{\textbf{12.307}} (0.373) & \textcolor[HTML]{A46500}{\textbf{44.342}} (0.820) \\
\midrule
\multirow{3}{*}{ICNNq (ReLU)} & $(64 \times 2)$ & 1.754 (0.042) & 10.111 (0.121) & \textcolor[HTML]{E56B00}{\textbf{25.761}} (0.543) \\
 & $(64 \times 4)$ & \textcolor[HTML]{E56B00}{\textbf{1.435}} (0.049) & \textcolor[HTML]{E56B00}{\textbf{8.165}} (0.616) & 437.974 (50.407) \\
 & $(64 \times 6)$ & 1.746 (0.155) & 22.471 (3.388) & $1.82 \cdot 10^{4}$ (2400.253) \\
\midrule
\multirow{9}{*}{ICNNq (Softplus)} & $(64 \times 2)$; $\tau = 0.1$ & 0.878 (0.038) & 8.627 (0.049) & 26.297 (0.826) \\
 & $(64 \times 2)$; $\tau = 1$ & \underline{0.546} (0.064) & 7.295 (0.422) & 26.434 (0.609) \\
 & $(64 \times 2)$; $\tau = 10$ & 3.544 (0.021) & 7.969 (0.035) & 22.885 (0.060) \\
 & $(64 \times 4)$; $\tau = 0.1$ & 0.722 (0.012) & 5.543 (0.209) & 53.773 (3.493) \\
 & $(64 \times 4)$; $\tau = 1$ & \textcolor[HTML]{8B1301}{\underline{\textbf{0.360}}} (0.011) & \underline{3.532} (0.440) & 36.023 (0.716) \\
 & $(64 \times 4)$; $\tau = 10$ & 3.348 (0.044) & 7.731 (0.036) & 22.116 (0.037) \\
 & $(64 \times 6)$; $\tau = 0.1$ & 0.812 (0.030) & \underline{5.330} (0.183) & $2.96 \cdot 10^{3}$ (1116.051) \\
 & $(64 \times 6)$; $\tau = 1$ & \underline{0.412} (0.025) & \textcolor[HTML]{8B1301}{\underline{\textbf{1.913}}} (0.187) & 30.990 (0.838) \\
 & $(64 \times 6)$; $\tau = 10$ & 3.437 (0.037) & 7.611 (0.027) & \textcolor[HTML]{8B1301}{\textbf{21.854}} (0.067) \\
\midrule
\multirow{3}{*}{HyCNN} & $(48 \times 2)$ & 2.536 (0.166) & 7.850 (0.019) & \underline{20.435} (0.069) \\
 & $(48 \times 4)$ & 1.711 (0.190) & \textcolor[HTML]{0080DB}{\textbf{7.775}} (0.015) & \textcolor[HTML]{0080DB}{\underline{\textbf{19.808}}} (0.047) \\
 & $(48 \times 6)$ & \textcolor[HTML]{0080DB}{\textbf{0.822}} (0.027) & 7.894 (0.028) & \underline{20.126} (0.059) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
\begin{table}[h!]
\caption{Sinkhorn divergence (mean and SE over $10$ runs) of the estimated OT map for the OT map (d) $\textstyle T_4(\bx) = (4x_i^3)_{i \in [d]}$. Per HyCNN architecture ($48 \times L$) and per dimension, the $\tau$ variant with the smallest mean Sinkhorn divergence is bold and colored, with the \underline{three smallest} values across all HyCNN rows underlined.}
\label{tab:ot_sinkhorn_full_psi3}
\scriptsize
\makebox[\textwidth][c]{%
\begin{tabular}{llccc}
\toprule
\multicolumn{2}{c}{HyCNN architecture $\backslash$ $d$} & 10 & 20 & 50 \\
\midrule
 & $(48 \times 2)$; $\tau = 0.1$ & \underline{\textbf{9.730}} (0.093) & 37.941 (0.149) & 140.750 (0.394) \\
 & $(48 \times 2)$; $\tau = 1$ & 10.667 (0.026) & 36.569 (0.101) & 133.017 (0.673) \\
 & $(48 \times 2)$; $\tau = 10$ & 10.445 (0.036) & \underline{\textbf{35.214}} (0.077) & \underline{\textbf{132.086}} (0.175) \\ \hline
 & $(48 \times 4)$; $\tau = 0.1$ & \underline{\textbf{9.687}} (0.136) & 37.262 (0.094) & 145.637 (0.470) \\
 & $(48 \times 4)$; $\tau = 1$ & 10.555 (0.032) & 35.749 (0.079) & 135.593 (0.180) \\
 & $(48 \times 4)$; $\tau = 10$ & 10.446 (0.035) & \textcolor[HTML]{0080DB}{\underline{\textbf{35.068}}} (0.080) & \textcolor[HTML]{0080DB}{\underline{\textbf{131.120}}} (0.189) \\ \hline
 & $(48 \times 6)$; $\tau = 0.1$ & \textcolor[HTML]{0080DB}{\underline{\textbf{9.199}}} (0.044) & 37.335 (0.140) & 144.029 (0.512) \\
 & $(48 \times 6)$; $\tau = 1$ & 10.504 (0.036) & 35.474 (0.084) & 132.464 (0.191) \\
 & $(48 \times 6)$; $\tau = 10$ & 10.461 (0.041) & \underline{\textbf{35.142}} (0.085) & \underline{\textbf{131.391}} (0.185) \\
\bottomrule
\end{tabular}%
}
\end{table}

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%
%

\clearpage
\renewcommand{\parabold}[1]{\paragraph{#1.}}
\section{Single Cell RNA-seq Data Analysis}\label{app:single_cell}

%

A central task in modern functional genomics and drug discovery is to predict how a population of cells responds to an external perturbation such as a chemical compound, a genetic intervention, or a change in culture conditions. Because most profiling technologies (single-cell RNA sequencing, mass cytometry, multiplexed imaging) destroy the cell upon measurement, one cannot observe the same cell before and after treatment. As a consequence, the unperturbed \emph{control} population and the \emph{perturbed} population are only accessible through two independent collections of single-cell measurements, and the learning problem is intrinsically one of matching \emph{distributions} rather than individual pairs of data points. This viewpoint is advocated by \citet{schiebinger2019optimal}, who used optimal transport to infer developmental trajectories from unpaired snapshots of single-cell gene expression during reprogramming, and was subsequently taken up in a series of works on perturbation response modeling, most notably \citet{bunne2023learning}. These works established optimal transport as a natural and principled language for formulating single-cell response prediction.

\paragraph{The 4i dataset}

The dataset we consider is the multiplexed imaging dataset of \citet{bunne2023learning}, obtained from the \emph{iterative indirect immunofluorescence imaging} (4i) technology. It is based on the sequential application of indirect immunofluorescence staining cycles to the same specimen, which allows a very large number of protein markers to be probed on the same set of cells. The result is a high-dimensional, single-cell-resolved readout of the proteomic state of each cell under control and under a wide range of drug treatments, made available by \citet{bunne2023learning} in a preprocessed form that we use without further modification. For each drug treatment we obtain two point clouds in a common feature space, one from the control population and one from the cells that were exposed to a drug, with sample sizes between roughly $1{,}300$ and $3{,}000$ cells per treatment (see \Cref{tab:4i-bestval-SD-n50}).

\paragraph{Mathematical task}

Denote by $P$ the distribution of the control cell population and by $Q_D$ the distribution of the cell population after exposure to drug $D$. We are given measurements $\bX_1, \dots, \bX_n$ from the control cell population and after treatment $D$, denoted by $\bY_1, \dots, \bY_m$, which we model as independent and identically distributed realizations from $P$ and $Q_D$, respectively.  We wish to construct an estimator $\hat T \colon \RR^p \to \RR^p$ such that the pushforward $\hat T_{\#} P$ is as close as possible to $Q_D$. The estimator is evaluated on a held-out test partition consisting of samples from both $P$ and $Q_D$, and the quality of the fit is measured by the Sinkhorn divergence, a geometrically meaningful two-sample discrepancy measure between probability distributions \citep{feydy2019interpolating,peyre2019computational}, between the predicted pushforward $\hat T_{\#} \hat P_{\mathrm{test}}$ and $\hat Q_{D,\mathrm{test}}$. 



\paragraph{Why optimal transport}

Among distribution matching methodologies, optimal transport is particularly appealing in this setting for two reasons. Conceptually, the static OT map minimizes the expected squared displacement and thus embodies the biological belief that cells evolve and proliferate along minimal-effort trajectories in feature space, rather than being reshuffled arbitrarily. This heuristic is motivated by the presence of an underlying potential, which drives the development and change of cells as they undergo the effects of a treatment. Methodologically, OT has been repeatedly reported to perform well as a predictive framework for single-cell perturbation response, starting from the developmental-trajectory analysis of \citet{schiebinger2019optimal} and including the neural OT approach of \citet{bunne2023learning}, among others. We therefore adopt neural OT map estimation as the basis of our analysis and compare our HyCNN architecture against the most competitive convex neural OT baseline identified in our synthetic experiments.



\paragraph{Concrete modeling choices}

For each drug $D$, we train two families of neural OT estimators to map the control distribution onto the perturbed distribution: a HyCNN of width $48$ and depth $L = 4$, and an ICNN of width $64$ and depth $L = 4$ equipped with softplus activations and a quadratic term in the first layer (ICNN(sm+q)). The ICNN(sm+q) variant consistently emerged as one of the strongest convex neural baselines in our synthetic OT experiments, see \Cref{app:OT_experiments}, which motivates its use as the reference competitor here. The width--depth configuration $64 \times 4$ was chosen because depth four has become a de facto standard in the neural OT literature \citep{makkuva2020optimal,bunne2023learning,uscidda2023monge}, and because the corresponding width of HyCNNs yields models whose capacity is comparable to the ICNN. For the HyCNN, we employ a smooth log-sum-exp activation with a smoothness parameter $\tau = 1$, a choice that is capable of adapting to smooth structure while remaining flexible. The ICNN uses standard softplus activations for the same reason and includes a quadratic term in the first layer, which lead to performance improvements in our experiments. 


\paragraph{Learning algorithm}

For training, we first split the control and drug cell data into $70\%-10\%-20\%$ for training, validation, and testing, respectively. We estimate the OT map using the variational semi-dual formulation as in \eqref{eq:HyCNN_OT_potential_estimation} for HyCNN and \eqref{eq:ICNN_objective} for ICNN, in which the outer and inner potentials are both parameterized by a HyCNN or ICNN. For the HyCNN and ICNN, we impose essentially the same learning algorithm as in \Cref{app:OT_implementation}. To assess the effect of the training budget, we consider two complementary schedules that are applied identically to both architectures. The \emph{short} schedule trains the networks for $T = 1{,}000$ outer iterations with $S = 5$ inner iterations per outer step, using the Adam optimizer with $\beta_1 = 0.5$, $\beta_2 = 0.9$, initial learning rate $\lambda = 10^{-2}$, and a cosine schedule with final learning-rate ratio $10^{-2}$. The \emph{long} schedule trains the networks for $T = 50{,}000$ outer iterations with $S = 10$ inner iterations per outer step, using the Adam optimizer with the same momentum parameters and a constant learning rate $\lambda = 5\times 10^{-4}$. The long schedule is roughly $100$ times more expensive than the short one (per-treatment training times of approximately $40$s, $60$s, $2$h, and $3$h for the short ICNN, short HyCNN, long ICNN, and long HyCNN, respectively, on our hardware); for this reason the long schedule is run for a single random seed per treatment, whereas the short schedule is repeated for $50$ seeds. All remaining hyperparameters are kept identical across the two architectures to keep the comparison as controlled as possible.

\paragraph{Evaluation and model selection}

To monitor and select models during training, we evaluate each candidate on a dedicated validation partition drawn from the training set. The validation criterion is the Sinkhorn divergence $\mathcal{S}{\epsilon}$ with squared Euclidean cost and regularization $\epsilon = 0.1$ \citep{feydy2019interpolating,peyre2019computational} between the predicted pushforward $\hat T_{\#} \hat P_{\mathrm{val}}$ and the ground-truth validation target $\hat Q_{D,\mathrm{val}}$. 
Validation losses are recorded every $10$ outer iterations under the short schedule, yielding $100$ candidate checkpoints per run, and every $100$ outer iterations under the long schedule, yielding $500$ candidate checkpoints per run. For each run, we identify the $K = 10$ checkpoints with the smallest validation Sinkhorn divergence and report the mean test Sinkhorn divergence over the $20\%$ held-out test partition. Averaging over the ten best-validation checkpoints, rather than selecting the single best one, ensures that the reported value reflects an entire neighborhood of the validation optimum and confirms that the comparison is stable along the training trajectory rather than an artifact of a single lucky checkpoint.
This \emph{best-validation averaging} rule is applied identically to both architectures. Under the short schedule, we repeat each experiment over $50$ random seeds governing data splits and network initialization, and report cross-seed means together with standard errors. Under the long schedule, the same rule applies, but due to the substantially higher per-run computational cost, we conduct only a single run per treatment, so no standard error is reported.

\paragraph{Results and discussion}

The resulting test-set Sinkhorn divergences are collected in \Cref{tab:4i-bestval-SD-n50}, which reports both training schedules for each of the $35$ drug treatments. Each table entry is the test-set Sinkhorn divergence averaged over the $K = 10$ checkpoints with the smallest validation loss along the corresponding training run, and this best-validation averaging is applied identically to both architectures and both schedules. The left two columns show, for each treatment, the cross-seed mean of this checkpoint-averaged quantity (with standard error in parentheses) over $50$ random seeds under the short schedule. The right two columns show the same checkpoint-averaged quantity for the single random-seed run under the long schedule, for which no standard error is reported. The results of the first seed of the short schedule, together with the long-schedule run, are visualized as grouped bar charts in \Cref{fig:HyCNN_training_OT}\textbf{(b)}; see \Cref{fig:HyCNN_training_OT_large} for an enlarged version. In the figures, treatments are ordered by short HyCNN test performance.

Three patterns emerge consistently from \Cref{tab:4i-bestval-SD-n50}. First, HyCNN attains a smaller test-set Sinkhorn divergence than ICNN consistently across treatments and schedules. Under the short schedule, HyCNN strictly improves over ICNN on all $35$ treatments, with (cross-seed) mean improvements that are typically on the order of $25$–$40\%$ and outside one standard error. Under the long schedule, HyCNN remains the better architecture on $32$ of the $35$ treatments, with the three exceptions (Imatinib, Pomalidomide-carfilzomib-dexamethasone, and Regorafenib) showing only marginal differences in favor of ICNN. Since each entry already averages over the ten best validation checkpoints, these observations cannot be attributed to a single checkpoint but instead reflect a consistent separation between the two architectures along their respective training trajectories. Second, the long schedule lowers the test-set Sinkhorn divergence relative to the short schedule across nearly every treatment for both architectures, confirming that the additional optimization budget is genuinely informative rather than an artifact of the learning-rate schedule. Third, the short HyCNN performs competitively with the long ICNN despite using roughly $100$ times less compute. It matches or improves upon the long ICNN on $13$ of the $35$ treatments and is often outperformed only by small margins on the remaining ones. Altogether, these findings indicate that, within the neural OT framework, replacing the ICNN potential by a HyCNN consistently improves the distributional fit, and that this improvement is not an artifact of an under-trained ICNN baseline. This is a useful insight for practitioners of neural OT in single-cell applications, as the resulting gain comes at only a slight additional per-iteration cost due to the two-gate architecture of HyCNN blocks.

\begin{table}[t!]
\centering
\caption{Sample sizes and test-set prediction errors across drug treatments for ICNN ($64\times4$) with softplus ($\tau = 1$) and a quadratic term in the first layer, and HyCNN ($48\times 4$) with logsumexp ($\tau = 1$). The two architectures are compared under two training budgets: the short run ($T = 1{,}000$ outer iterations, $S = 5$ inner steps, initial learning rate $\lambda = 0.01$, final learning-rate ratio $0.01$ under a cosine scheduler), and the long run ($T = 50{,}000$ outer iterations, $S = 10$ inner steps, constant learning rate $\lambda = 5\times 10^{-4}$). For each drug, we report the test-set Sinkhorn divergence ($\epsilon = 0.1$) on a $20\%$ test partition, averaged over the $K = 10$ checkpoints with smallest loss on a $10\%$ validation partition; validation losses are recorded every $10$ outer iterations under the short schedule and every $100$ outer iterations under the long schedule. The left two columns report the cross-seed mean of this checkpoint-averaged quantity (with standard error in parentheses) across $50$ random seeds; the right two columns report the same checkpoint-averaged quantity for the single long-schedule run per treatment. Bold indicates the smaller mean within each $(T, S)$ pair.     Treatments are abbreviated as in Figure \ref{fig:HyCNN_training_OT_large}, further recall that Figure \ref{fig:HyCNN_training_OT_large} only displays the fit for the first train/validation/test split along all methods, whereas here only for the long runs this split is considered.}
\label{tab:4i-bestval-SD-n50}
\makebox[\textwidth][c]{%
\resizebox{\textwidth}{!}{%
\begin{tabular}{|c|c|l l|c c|}
\hline
\multirow{3}{*}{Treatment} & \multirow{3}{*}{Sample size} & \multicolumn{4}{|c|}{\textcolor{white}{$e^{e^{e^e}}$}Sinkhorn Divergence~($\epsilon = 0.1$)\textcolor{white}{$e^{e^{e^e}}$}} \\[0.05cm]
 & & \multicolumn{1}{|c}{ICNN(sp+q)} & \multicolumn{1}{c|}{HyCNN}& \multicolumn{1}{c}{ICNN(sp+q)} & \multicolumn{1}{c|}{HyCNN} \\[0.05cm]
 &&\multicolumn{2}{|c|}{$(T = 1{,}000,\ S = 5)$}  & \multicolumn{2}{c|}{$(T = 50{,}000,\ S = 10)$} \\[0.05cm]
\hline
\textcolor{white}{$e^{e^{e^e}}$}Cisplatin\textcolor{white}{$e^{e^{e^e}}$} & 2693 & 2.86~(0.63) & \textbf{1.75~(0.011)} & 1.69 & \textbf{1.65} \\
Cisp-olap & 2245 & 2.65~(0.13) & \textbf{2.05~(0.018)} & 1.97 & \textbf{1.95} \\
Crizotinib & 1978 & 5.35~(0.97) & \textbf{3.17~(0.039)} & 3.00 & \textbf{2.90} \\
Dabrafenib & 2675 & 2.57~(0.41) & \textbf{1.65~(0.012)} & 1.64 & \textbf{1.56} \\
Dacarbazine & 2485 & 2.49~(0.25) & \textbf{1.68~(0.013)} & 1.71 & \textbf{1.64} \\
Dasatinib & 2250 & 5.13~(0.55) & \textbf{3.18~(0.039)} & 2.75 & \textbf{2.70} \\
Decitabine & 2648 & 2.54~(0.16) & \textbf{1.92~(0.014)} & 1.80 & \textbf{1.73} \\
Dexamethasone & 2796 & 2.88~(0.29) & \textbf{1.94~(0.018)} & 1.93 & \textbf{1.84} \\
Erlotinib & 2406 & 3.32~(0.47) & \textbf{1.91~(0.014)} & 1.84 & \textbf{1.77} \\
Everolimus & 2592 & 3.23~(0.60) & \textbf{1.86~(0.012)} & 1.88 & \textbf{1.68} \\
Hydroxyurea & 2715 & 2.95~(0.35) & \textbf{1.99~(0.012)} & 2.08 & \textbf{2.03} \\
Imatinib & 2631 & 3.24~(0.30) & \textbf{2.33~(0.023)} & \textbf{2.00} & 2.01 \\
Ixazomib & 2514 & 3.72~(0.18) & \textbf{2.81~(0.021)} & 2.62 & \textbf{2.44} \\
Ixa-Lenal-Dexa & 2522 & 3.40~(0.32) & \textbf{2.16~(0.012)} & 2.20 & \textbf{2.10} \\
Lenalidomide & 2524 & 2.36~(0.26) & \textbf{1.56~(0.010)} & 1.65 & \textbf{1.55} \\
Melphalan & 2352 & 3.75~(1.3) & \textbf{1.71~(0.012)} & 1.65 & \textbf{1.53} \\
Midostaurin & 2425 & 3.24~(0.26) & \textbf{2.08~(0.017)} & 1.94 & \textbf{1.75} \\
Mln2480 & 2367 & 2.47~(0.30) & \textbf{1.56~(0.014)} & 1.64 & \textbf{1.57} \\
Olaparib & 2540 & 3.50~(0.54) & \textbf{2.01~(0.016)} & 1.86 & \textbf{1.82} \\
Paclitaxel & 2636 & 4.72~(1.2) & \textbf{2.76~(0.018)} & 2.51 & \textbf{2.45} \\
Palbociclib & 2322 & 3.01~(0.40) & \textbf{1.90~(0.014)} & 1.83 & \textbf{1.74} \\
Panobinostat & 2492 & 2.95~(0.34) & \textbf{1.92~(0.022)} & 1.70 & \textbf{1.56} \\
Poma-Carfil-Dexa & 2545 & 3.82~(0.23) & \textbf{2.70~(0.025)} & \textbf{2.61} & 2.68 \\
Regorafenib & 2524 & 4.91~(1.7) & \textbf{1.76~(0.012)} & \textbf{1.71} & 1.76 \\
Sorafenib & 2763 & 3.02~(0.53) & \textbf{1.65~(0.012)} & 1.69 & \textbf{1.61} \\
Staurosporine & 1310 & 13.94~(8.8) & \textbf{4.05~(0.041)} & 3.55 & \textbf{3.54} \\
Temozolomide & 2513 & 7.90~(5.5) & \textbf{1.93~(0.017)} & 2.21 & \textbf{1.95} \\
Trametinib & 2637 & 3.42~(1.1) & \textbf{1.38~(0.0094)} & 1.41 & \textbf{1.30} \\
Tram-dabra & 2958 & 2.23~(0.30) & \textbf{1.32~(0.011)} & 1.34 & \textbf{1.30} \\
Tram-erlot & 2452 & 2.07~(0.14) & \textbf{1.39~(0.0092)} & 1.47 & \textbf{1.36} \\
Tram-midos & 2211 & 5.60~(1.3) & \textbf{2.62~(0.026)} & 2.07 & \textbf{2.01} \\
Tram-panob & 2377 & 2.52~(0.37) & \textbf{1.57~(0.017)} & 1.34 & \textbf{1.31} \\
Ulixertinib & 2858 & 2.27~(0.14) & \textbf{1.79~(0.016)} & 1.94 & \textbf{1.66} \\
Vem-cobimet & 2695 & 2.70~(0.17) & \textbf{1.93~(0.017)} & 1.94 & \textbf{1.81} \\
Vindesine & 2102 & 3.49~(0.41) & \textbf{2.66~(0.025)} & 2.27 & \textbf{2.19} \\
\hline
\end{tabular}}}
\end{table}

\begin{figure}[t!]
%
  \begin{center}
    \centerline{%
    %
    \includegraphics[width=\textwidth, trim = 0 0 0 0, clip]{../figures/FIG_4i_OT_combined_sd_all_large_every100_kbest10.pdf}}
    %
    \caption{Enlarged view of Figure \ref{fig:HyCNN_training_OT}\textbf{(b)} with drug labels on the $x$-axis. Sinkhorn divergence between predicted and ground-truth drug-perturbed distributions on a $20\%$ held-out test partition of the 4i dataset for each drug, based on ICNN ($64\times4$, Softplus, $\tau = 1$, quad) and HyCNN ($48\times 4$, logsumexp, $\tau = 1$), trained for $T = 1{,}000$ outer iterations with $S = 5$ inner iterations (short) and $T = 50{,}000$ outer iterations with $S = 10$ inner iterations (long). For each architecture and schedule, the displayed value is the test-set Sinkhorn divergence averaged over the $K = 10$ checkpoints with smallest validation loss along the corresponding training run. Per treatment, the distributional fit is computed on a fixed train/validation/test split, we do this to ensure a fair comparison among methods. This also explains why the values for the short runs slightly deviate from the cross-seed means reported in \Cref{tab:4i-bestval-SD-n50}.  
    In~the figure use the following abbreviations for treatments: Cisp-olap for Cisplatin-olaparib, Ixa-Lenal-Dexa for Ixazomib-lenalidomide-dexamethasone, Poma-Carfil-Dexa for Pomalidomide-carfilzomib-dexamethasone, Tram-dabra for Trametinib-dabrafenib, Tram-erlot for Trametinib-erlotinib, Tram-midos for Trametinib-midostaurin, Tram-panob for Trametinib-panobinostat, and Vem-cobimet for Vemurafenib-cobimetinib.
    %
    }\label{fig:HyCNN_training_OT_large}
  \end{center}
\end{figure}

\parabold{CellOT and future directions}
For context, the CellOT pipeline of \citet{bunne2023learning} trains the ICNN-based neural OT model for substantially more iterations than the $50{,}000$ outer steps used in our long schedule; for instance, \citet{bunne2023learning} use $T = 250{,}000$ iterations with $S = 10$ inner loops at a constant learning rate of $10^{-4}$. Our long schedule already addresses much of the concern that the ICNN baseline could simply be under-trained: increasing the ICNN budget from $1{,}000$ to $50{,}000$ outer iterations narrows its absolute error noticeably, yet HyCNN remains the better architecture on $32$ of the $35$ treatments under the long schedule, and the short HyCNN remains broadly competitive with the long ICNN despite using $100$ times less compute. Since both architectures continue to benefit from additional training while preserving this ordering, we expect a full $250{,}000$-iteration evaluation against the CellOT baseline to reinforce rather than overturn our qualitative picture reported here. A comprehensive comparison with a larger budget is, therefore, a natural next step.

    \end{document}
