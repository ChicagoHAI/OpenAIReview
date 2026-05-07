\documentclass{article}
\usepackage{graphicx} 
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}  
\usepackage{amsfonts} 
\usepackage{amsthm}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{algorithm}
\usepackage{natbib}
\usepackage{algpseudocode}
\usepackage{longtable}
\usepackage[margin=1in]{geometry}


\newtheorem{theorem}{Theorem}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}{Lemma}
\newtheorem{example}{Example}
\newtheorem{corollary}{Corollary}
\newtheorem{assumption}{Assumption}
\newtheorem*{assumption*}{Assumption}
\DeclareMathOperator{\Var}{Var}
\DeclareMathOperator{\E}{E}
\DeclareMathOperator{\Cov}{Cov}
\DeclareMathOperator{\Corr}{Corr}
\DeclareMathOperator{\argmax}{argmax}

\title{Multivariate incremental effects for continuous treatments: Studying the health effects of environmental mixtures}

\author{%
  Zhuochao Huang\thanks{Department of Statistics, University of Florida. 
    Corresponding author: Zhuochao Huang, \texttt{zhuochao.huang@ufl.edu}}%
  \and Kejin Dong\footnotemark[1]%
  \and Tuo Lin\thanks{Department of Biostatistics, University of Florida.}%
  \and Joseph Antonelli\footnotemark[1]%
}
\date{}
\begin{document}
\maketitle

\begin{abstract}
Evaluating the causal health effects of multivariate, continuous exposures, such as air pollution mixtures, is a critical public health challenge. A primary obstacle is the frequent violation of the positivity assumption, which renders the effects of standard deterministic interventions unidentified or heavily reliant on unreliable model extrapolation. In this paper, we develop a novel causal inference framework to address this challenge. We extend exponential tilting to multivariate exposures and address the critical question of how to compare different intervention directions fairly. This establishes a systematic framework for defining and evaluating various policy-relevant causal estimands, allowing researchers to address diverse scientific questions. We develop numerous methodological advancements, including efficient one-step estimation strategies, a Riemannian BFGS algorithm to solve a constrained manifold optimization problem, semiparametric efficiency bounds for causal estimands, minimax rates for estimators, and asymptotic normality results. We demonstrate our framework's utility by applying it to a nationwide environmental health dataset to identify the optimal strategy for reducing adverse health outcomes associated with a PM$_{2.5}$ chemical mixture.
\end{abstract}

\section{Introduction}

Understanding the causal effects of complex air exposure mixtures is crucial for effective public health policy, but traditional statistical methods face significant challenges. A key challenge is that individuals are exposed to a complex mixture of correlated substances. Single-pollutant analyses often fall short, as they fail to account for the confounding effect of pollutants and cannot capture potential interaction effects, leading to misleading policy recommendations \citep{bobb2015causal,antonelli2024causal}. This necessitates a causal inference framework for multivariate continuous exposures. A primary obstacle in evaluating the causal effects of multivariate continuous exposures is the positivity assumption. This assumption requires that for any given set of covariates, the exposure levels of interest have nonzero density. In environmental mixtures, this assumption is frequently violated; certain combinations of pollutants may be physically implausible or absent from observational data \citep{peters2012causal}. Consequently, estimating the effect of deterministic interventions, such as setting a pollutant mixture to a specific counterfactual level, becomes impossible without resorting to unreliable extrapolation \citep{antonelli2024causal, rudolph2025everything}. In the presence of positivity violations, there are (at least) two potential solutions. The less frequently used approach is to modify the estimation method to be robust to extrapolation, such as ``extrapolation-aware" inferential methods that explicitly bound or characterize the uncertainty when moving outside the data support \citep{pfister2021extrapolation}. The more common approach, and the one we focus on throughout, is to modify the scientific question by redefining the estimand. 

One useful strategy for modifying the estimand with continuous treatments involves identifying and estimating the derivative of the exposure-response function, then integrating this derivative to recover the full curve. By focusing on local effects first and developing novel bias-corrected and Neyman Orthogonal estimators for the derivative function, this ``differentiate-then-integrate" approach can circumvent the need for a global positivity assumption and has been a subject of significant recent research \citep{zhang2023nonparametric, kallus2022doubly, rothenhausler2021incremental}. Another alternative is to leverage instrumental variables, where recent advances have extended these methods to continuous treatments without relying on positivity to identify local effects \citep{dorn2024nonparametric, bruns2024local}.

While these methods are powerful, a distinct set of approaches that are flexible and policy-relevant rely on the use of stochastic interventions. These interventions generally define a policy that modifies the observed distribution of exposures rather than replacing it with a fixed value. Motivated by defining more realistic policies, early applications have been seen in epidemiology. For example, considering interventions that would truncate the exposure distribution, such as enforcing pollution levels below a certain cutoff \citep{taubman2009intervening}. This idea was later formalized in the statistical literature to provide a general framework for evaluating the population causal effect of shifting an entire exposure distribution \citep{diaz2012population}. Over the past decade, several distinct stochastic interventions have been developed. One approach is the shift intervention, which defines the post-intervention exposure as the natural exposure value shifted by a certain amount \citep{haneuse2013estimation}. A second, influential family of interventions is based on the natural value of treatment. These policies, often called Modified Treatment Policies (MTPs), define the counterfactual exposure as a function of the exposure that would have naturally occurred. This concept was pioneered in the context of dynamic treatment regimes \citep{robins2004effects} and later formalized for single time points \citep{young2011identification, richardson2013single}. The framework has since been extended to handle longitudinal scenarios with continuous treatments \citep{diaz2023nonparametric}. There is ongoing research exploring the properties of generalized policies that depend on an individual's natural value of treatment, for example using optimal transport to derive tighter bounds under unmeasured confounding \citep{kallus2024stochastic}. Generally speaking, this class of estimands relies on weaker positivity conditions than most deterministic estimands, however, they still rely on positivity holding for certain exposure values.

When positivity violations are a big concern and are likely to occur, a potentially more robust alternative that inherently respects the data's support and thereby does not rely on positivity is the incremental intervention. This approach was initially developed for binary and longitudinal treatments through incremental shifts in propensity scores, and defines a new interventional distribution by tilting the exposure distribution with an exponential function in a specified direction \citep{kennedy2019nonparametric}. This concept has subsequently been generalized to univariate continuous treatments as well \citep{diaz2020causal,schindl2024incremental}. Some recent work has criticized exponential tilted estimands such as these \citep{schindl2025causal} due to their less intuitive parameterization, asymmetric reallocation of probability mass, and for possessing less favorable asymptotic properties compared to certain alternatives. Regardless of their form, stochastic interventions, typically present their own set of challenges. One key concern is that estimands identified under positivity violations may correspond to interventions that are not directly implementable, revealing a fundamental ``interpretability-implementability tradeoff'' \citep{rudolph2024propensity}. Furthermore, when comparing the effects of different stochastic interventions, one must ensure the comparisons are fair, a concept that related work in different contexts has begun to formalize to prevent misleading conclusions \citep{mcclean2024fair}.

Nearly all work to date has focused on univariate treatments, which is insufficient for addressing problems raised in the analysis of environmental mixtures. In this work, we build on the existing literature by using exponentially tilted estimands within the multivariate treatment context. This extension to the multivariate setting is non-trivial and introduces several new, complex questions. First, the intervention parameter becomes a vector, creating an infinite space of possible intervention directions. This raises a variety of policy questions about how to shift all exposures at once and which direction is best. Second, a fair basis for comparing these different directional shifts is needed; interventions must be constrained to be of the same size for meaningful comparisons, where the definition of fair is not unique. We propose solutions to each of these issues and explore a variety of estimands within this framework that target different policy-relevant questions of interest in environmental epidemiology. We show that these different estimands vary in terms of how efficiently they can be estimated from the data, and we provide algorithms for finding optimal policies in terms of shifts in exposures that lead to the biggest reduction in adverse health outcomes. We provide theoretical support in terms of minimax rates that show how well the estimands can be estimated and how the difficulty of estimation intrinsically depends on the conditional covariance matrix of the exposures. We also develop efficient influence function based estimators that can achieve root-$n$ convergence and asymptotic normality using complex, machine learning estimators for nuisance function estimation. 


% Our work builds upon exponential tilting framework, and we acknowledge an ongoing discussion in the literature regarding the optimal construction of stochastic intervention paths. Most recent ``causal geodesy'' framework proposes viewing interventions as paths on a statistical manifold, arguing that geodesic between observational and target distributions may hold superior properties \citep{schindl2025causal}. From this geometric perspective, the exponential tilt has been critiqued for its less intuitive parameterization, its asymmetric reallocation of probability mass, and for possessing less favorable asymptotic properties compared to certain geodesic alternatives like the Wasserstein intervention. Despite these valid critiques, we contend that the exponential tilt remains a powerful and pragmatic choice for the specific challenges posed by multivariate environmental mixtures. Its foremost advantage is its inherent robustness to positivity violations, as it naturally respects the support while Wasserstein tilt requires a global positivity assumption that is often untenable. For a problem as complex as navigating an infinite space of multivariate intervention directions ($\boldsymbol{\delta}$) and establishing their fair comparison, the mathematical tractability and well-understood properties of the exponential tilt provide an indispensable foundation, contrary to the Hellinger tilt proposed in \citep{schindl2025causal}. Our contribution, therefore, is not to claim discovery of an ``optimal path'' in the geodesic sense, but rather to characterize the landscape of directional causal effects within a robust and applicable framework---a task for which the exponential tilting mechanism is particularly well-suited.

% The remainder of the paper is organized as follows. Section 2 introduces our formal framework, including notation, assumptions, and causal estimands. Section 3 develops our estimation and inference procedures. Section 4 presents simulation studies, and Section 5 applies our method to real-world air pollution data. We conclude with a discussion of limitations and future directions.



\section{Exposure Shifts under Exponential Tilts}
\label{sec:Estimands}

\subsection{Notation and Potential Outcomes under SUTVA}

Let our observed data consist of $n$ independent and identically distributed samples $\{\boldsymbol{Z}_i\}_{i=1}^n$, drawn from some underlying distribution $P_0$. Each observation $\boldsymbol{Z}_i = (\boldsymbol{X}_i, \boldsymbol{W}_i, Y_i)$ is composed of a $p$-dimensional vector of covariates $\boldsymbol{X}_i \in \mathcal{X} \subseteq \mathbb{R}^p$, a $q$-dimensional vector representing the environmental exposures or treatments\footnote{Note that we use the terms treatment and exposure interchangeably throughout the manuscript. Also note that environmental mixture simply refers to a vector of environmental exposures.} $\boldsymbol{W}_i = (W_{i1}, \dots, W_{iq}) \in \mathcal{W} \subseteq \mathbb{R}^q$, and a scalar outcome of interest $Y_i \in \mathbb{R}$. We denote the conditional density of the exposure mixture given the covariates as $f(\boldsymbol{w} \mid \boldsymbol{x})$.

To formally define causal effects, we operate within the potential outcomes framework. For each individual $i$ and any potential exposure vector $\boldsymbol{w} \in \mathcal{W}$, we let $Y_i(\boldsymbol{w})$ denote the potential outcome that would have been observed had individual $i$ received exposure level $\boldsymbol{w}$. This notation relies on the Stable Unit Treatment Value Assumption (SUTVA, \citep{rubin1980randomization}), which comprises two key principles:
\begin{enumerate}
    \item No Interference: The potential outcome for one individual is unaffected by the exposure assignments of other individuals. That is, $Y_i(\boldsymbol{w})$ depends only on the exposure $\boldsymbol{w}$ assigned to individual $i$.
    \item No multiple versions of treatment: Treatment is well-defined in the sense that there are not two distinct treatments that lead to the same value of $\boldsymbol{W}_i$.
\end{enumerate}
Importantly, this assumption ensures that an individual's observed outcome corresponds to their potential outcome under their observed exposure. Formally, if an individual $i$ is observed to have exposure $\boldsymbol{W}_i$, their observed outcome is $Y_i = Y_i(\boldsymbol{W}_i)$.

\subsection{Estimands using Exponential Tilts}

In this work, we extend the framework of exponential tilting incremental causal effects to the multivariate treatment setting. This type of stochastic treatment was first proposed for binary treatments \citep{kennedy2019nonparametric} and later generalized to single continuous treatments \citep{diaz2020causal, schindl2024incremental}. We adapt this formulation to define interventions on the entire $q$-dimensional exposure vector, $\boldsymbol{W}$. Given the conditional density of the exposure mixture, $f(\boldsymbol{w} \mid \boldsymbol{x})$, we define an exponentially tilted interventional density, $g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x})$, indexed by a user-specified vector $\boldsymbol{\delta} \in \mathbb{R}^q$:
\begin{equation}
    g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x}) = \frac{\exp(\boldsymbol{\delta}^\top \boldsymbol{w}) f(\boldsymbol{w} \mid \boldsymbol{x})}{\int_{\mathcal{W}} \exp(\boldsymbol{\delta}^\top \boldsymbol{v}) f(\boldsymbol{v} \mid \boldsymbol{x}) \, d\boldsymbol{v}}
    \label{eq:tilt}
\end{equation}
Here, the denominator is a normalizing constant that ensures $g_{\boldsymbol{\delta}}$ integrates to one, and $\boldsymbol{\delta}$ is a vector determining both the direction and magnitude of how the natural density is shifted.

Our causal estimand of interest, the incremental effect, is the expected potential outcome under the stochastic intervention defined by the tilted density $g_{\boldsymbol{\delta}}$. We denote this estimand as $\psi(\boldsymbol{\delta})$:
$$
\psi(\boldsymbol{\delta}) = \mathbb{E}[Y^{g_{\boldsymbol{\delta}}}]
$$
This represents the population average outcome if, for covariates $\boldsymbol{X}=\boldsymbol{x}$, each individual's exposure were a random draw from the shifted distribution $g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x})$. In order to identify this quantity from the observed data, we must make a standard no unmeasured confounding assumption: for all $\boldsymbol{w}\in\mathcal{W}$,
$$
Y(\boldsymbol{w})\perp \boldsymbol{W}\mid \boldsymbol{X}.
$$
We develop sensitivity analysis approaches to assess violations of this assumption in Section~\ref{sec:SensitivityFinal}. Under SUTVA and the no unmeasured confounding assumption, this causal quantity is identified from the observed data distribution via:
\begin{equation}
    \psi(\boldsymbol{\delta}) = \int_{\mathcal{X}} \int_{\mathcal{W}} \mathbb{E}[Y \mid \boldsymbol{W}=\boldsymbol{w}, \boldsymbol{X}=\boldsymbol{x}] \, g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x}) \, d\boldsymbol{w} \, dP(\boldsymbol{x})
    \label{eq:estimand}
\end{equation}
where $P(\boldsymbol{x})$ denotes the marginal probability measure of the covariates $\boldsymbol{X}$. Note that because the support of $g_{\boldsymbol{\delta}}$ is identical to the support of $f$, we do not have to invoke any positivity assumptions and the intervention does not require us to estimate outcomes for exposure combinations that are never observed in the data.

The parameter $\boldsymbol{\delta}$ has a similar interpretation as the constant gradient of the log-likelihood ratio between the interventional and observational densities as in \citep{schindl2024incremental}:
$$
\boldsymbol{\delta} = \frac{\partial}{\partial \boldsymbol{w}} \log \left( \frac{g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x})}{f(\boldsymbol{w} \mid \boldsymbol{x})} \right).
$$
This means that each component, $\delta_j$, quantifies the change in this log density ratio for an infinitesimal increase in the $j$-th exposure component, $w_j$. Intuitively, setting $\boldsymbol{\delta} = (1, 0, \dots, 0)^\top$ defines an intervention that tilts the distribution to favor higher values of the first exposure, $W_1$.



\subsection{Different Exposure Shifts and Efficiency}



Let $\mu(\boldsymbol{x}, \boldsymbol{w}) = \mathbb{E}[Y \mid \boldsymbol{X}=\boldsymbol{x}, \boldsymbol{W}=\boldsymbol{w}]$. Following the same derivation as \citep{schindl2024incremental} but generalized to the multivariate setting, we get the following formula for the efficient influence function.

\begin{proposition}
\label{prop:eif}
The efficient influence function of $\psi(\boldsymbol{\delta})$ under a nonparametric model is given by $\varphi(\boldsymbol{Z}; \boldsymbol{\delta}) = D_Y + D_{g,\mu} + D_{\psi}$ for
\begin{gather*}
    D_Y = \frac{g_{\boldsymbol{\delta}}(\boldsymbol{W} \mid \boldsymbol{X})}{f(\boldsymbol{W} \mid \boldsymbol{X})} \left( Y - \mu(\boldsymbol{X}, \boldsymbol{W}) \right) \\
    D_{g,\mu} = \frac{g_{\boldsymbol{\delta}}(\boldsymbol{W} \mid \boldsymbol{X})}{f(\boldsymbol{W} \mid \boldsymbol{X})} \left( \mu(\boldsymbol{X}, \boldsymbol{W}) - \mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu(\boldsymbol{X}, \boldsymbol{W}) \mid \boldsymbol{X}] \right) \\
    D_{\psi} = \mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu(\boldsymbol{X}, \boldsymbol{W}) \mid \boldsymbol{X}] - \psi
\end{gather*}
\end{proposition}
Note the subscript $g_{\boldsymbol{\delta}}$ denotes expectations with respect to the tilted exposure density. The asymptotic variance of any regular and asymptotically linear (RAL) estimator for $\psi(\boldsymbol{\delta})$ is equal to the variance of its EIF, $\mathrm{Var}(\varphi(\boldsymbol{Z}; \boldsymbol{\delta}))$. A critical observation from the structure of $\varphi$ is the repeated appearance of the density ratio, $g_{\boldsymbol{\delta}}(\boldsymbol{W} \mid \boldsymbol{X}) / f(\boldsymbol{W} \mid \boldsymbol{X})$. When this ratio exhibits high variability, it inflates the variance of the first two components of the EIF, leading to less precise estimates of the causal effect. Therefore, to improve statistical efficiency for a given intervention strength, we could select an intervention direction $\boldsymbol{\delta}$ that minimizes the variance of this density ratio, $\mathrm{Var}(g_{\boldsymbol{\delta}}/f)$. The third term, on the other hand, represents the deviation between the average post-intervention effect for a specific covariate group and the overall average post-intervention effect. It quantifies how much higher or lower the expected intervention effect for an individual with covariates $\boldsymbol{X}$ is compared to the overall population average. 

To gain analytical insight into this variance, we can let the exposures follow a multivariate normal distribution, $f(\boldsymbol{w} \mid \boldsymbol{x}) \sim \mathcal{N}(\boldsymbol{\mu_x}, \boldsymbol{\Sigma})$. Under this assumption, we have two key results. First, the tilted distribution $g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x})$ is also normal, with a shifted mean:
$$
g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x}) \sim \mathcal{N}(\boldsymbol{\mu_x} + \boldsymbol{\Sigma}\boldsymbol{\delta}, \boldsymbol{\Sigma})
$$
This provides a clear interpretation of the intervention: it is a shift of the mean of the exposure distribution in the direction $\boldsymbol{\Sigma}\boldsymbol{\delta}$. Second, the variance of the density ratio has a simple, closed-form expression:
$$
\mathrm{Var}\left( \frac{g_{\boldsymbol{\delta}}(\boldsymbol{W} \mid \boldsymbol{X})}{f(\boldsymbol{W} \mid \boldsymbol{X})} \right) = \exp(\boldsymbol{\delta}^\top \boldsymbol{\Sigma} \boldsymbol{\delta}) - 1
$$
Minimizing this variance is equivalent to minimizing the quadratic form $\boldsymbol{\delta}^\top \boldsymbol{\Sigma} \boldsymbol{\delta}$.

The question of interest thus becomes an optimization problem: which direction $\boldsymbol{\delta}$ minimizes $\boldsymbol{\delta}^\top \boldsymbol{\Sigma} \boldsymbol{\delta}$ subject to a constraint on the ``strength" of the intervention? While various constraints are possible (e.g., fixing $\boldsymbol{\delta}^\top\boldsymbol{\delta}$), a particularly meaningful constraint is to fix the distance between the original and tilted distributions, for which the 2-Wasserstein distance provides a natural metric. We discuss the choice of this metric in the following section. For the multivariate normal case with the same covariance matrix, the squared Wasserstein distance has a simple closed-form expression as $d_W^2(f, g_{\boldsymbol{\delta}}) = ||(\boldsymbol{\mu_x} + \boldsymbol{\Sigma}\boldsymbol{\delta}) - \boldsymbol{\mu_x}||^2 = ||\boldsymbol{\Sigma}\boldsymbol{\delta}||^2 = \boldsymbol{\delta}^\top \boldsymbol{\Sigma}^2 \boldsymbol{\delta}$.

If our goal then is to find a shift that we can estimate with a high degree of efficiency, we can solve the following:
$$
\min_{\boldsymbol{\delta}} \quad \boldsymbol{\delta}^\top \boldsymbol{\Sigma} \boldsymbol{\delta} \quad \text{subject to} \quad \boldsymbol{\delta}^\top \boldsymbol{\Sigma}^2 \boldsymbol{\delta} = c^2
$$
for some constant $c$ defining the size of intervention. It is straightforward to show that this expression is minimized when $\boldsymbol{\delta}$ is chosen to be proportional to the eigenvector of $\boldsymbol{\Sigma}$ corresponding to its largest eigenvalue, $\lambda_{\max}$. Hence our finding demonstrates that for a fixed intervention strength (as measured by the Wasserstein distance), the most statistically efficient causal effect to estimate, at least in terms of this density ratio, is the one that corresponds to shifting the exposure mixture along its primary axis of variation. Note that this result only holds exactly under a multivariate normal distribution, but we have seen empirically that this choice of $\boldsymbol{\delta}$ typically leads to efficient estimates of $\psi(\boldsymbol{\delta})$ under a variety of exposure distributions. 

\subsection{Fair Exposure Shifts under Fixed Gelbrich Distance}

A primary motivation for developing our framework is to answer policy-relevant questions, such as identifying the optimal way to modify an environmental exposure mixture to achieve the greatest public health benefit. This naturally leads to an optimization problem: finding the intervention vector $\boldsymbol{\delta}$ that maximizes (or minimizes) the causal estimand $\psi(\boldsymbol{\delta})$. However, a naive comparison across all possible $\boldsymbol{\delta}$ vectors is misleading. For any intervention direction that yields a beneficial effect, one could simply increase the intervention's strength, for example, by scaling the magnitude of $\boldsymbol{\delta}$ to produce an arbitrarily larger (or smaller) value of $\psi(\boldsymbol{\delta})$. This would invariably lead to trivial solutions that correspond to extreme, unrealistic shifts in the exposure distribution. A more relevant policy question is ``for a fixed amount of interventional effort, what is the best direction to apply that effort?''. To formalize this, we must first establish a fair basis for comparison, constraining our search to a set of interventions that are of the same size, which captures the actual movement of the exposure values, not just the magnitude of the parameter $\boldsymbol{\delta}$. Note that the notion of fairness here is with respect to the size of the intervention being applied, which differs from typical notions of fairness in causal inference or related fields, such as in recent work that defines a fairness criterion based on whether an estimand preserves the ordinal ranking of effects across all covariate subgroups.\citep{mcclean2024fair} 

In order to establish our notion of fairness between interventions, we can use the 2-Wasserstein distance, $d_W(f, g_{\boldsymbol{\delta}})$, which is widely studied and serves this purpose \citep{panaretos2019statistical}. Intuitively, the Wasserstein distance measures the minimum cost of transporting the probability mass of one distribution to match another, akin to the cost of moving a pile of dirt. By fixing the Wasserstein distance, we ensure that the total amount of shift between the old and new distributions is fixed. The optimization problem thus becomes a meaningful search for the $\boldsymbol{\delta}$ that minimizes $\psi(\boldsymbol{\delta})$ among all possible intervention directions of a comparable magnitude. This distributional fairness notion is widely used in both the operations and statistics research literatures. \citep{mohajerin2018data, blanchet2019quantifying, duchi2021learning, gao2023distributionally}

For analytical tractability, we rely on a well-established result providing a formula for the squared 2-Wasserstein distance $d_W^2$ based on the means ($\boldsymbol{\mu}_1, \boldsymbol{\mu}_2$) and covariance matrices ($\boldsymbol{\Sigma}_1, \boldsymbol{\Sigma}_2$) of two distributions $(P_1, P_2)$, which is referred to as the Gelbrich formula \citep{Gelbrich1990}. Crucially, this formula serves as a general lower bound for the true squared 2-Wasserstein distance between any two probability measures on $\mathbb{R}^q$ with finite second moments. Specifically, we have that
$$
d_W^2\left(P_1, P_2\right) \geq\left\|\boldsymbol{\mu}_1-\boldsymbol{\mu}_2\right\|^2+\operatorname{tr}\left(\boldsymbol{\Sigma}_1+\boldsymbol{\Sigma}_2-2\left(\boldsymbol{\Sigma}_1^{1 / 2} \boldsymbol{\Sigma}_2 \boldsymbol{\Sigma}_1^{1 / 2}\right)^{1 / 2}\right):=d_G^2\left(P_1, P_2\right)
$$
Furthermore, this bound becomes an exact equality for any two distributions belonging to the same family of elliptically contoured distributions, a class which notably includes all multivariate normal distributions as well as uniform distributions on ellipsoids. The tractability of the Gelbrich formula has invited various researchers to use it as a surrogate for the 2-Wasserstein distance, a method frequently employed to overcome
the computational complexity associated with the Wasserstein
metric \citep{kuhn2019wasserstein, hakobyan2024wasserstein}, since the empirical 2-Wasserstein distance lacks a closed-form formula from data and can only be approached by numerical methods \citep{panaretos2020invitation}. Moreover, the lower bound it provides has been shown to be tight in a fairly general situation against an upper bound derived for the 2-Wasserstein distance \citep{biswas2024bounding, papp2024scalable}, and is therefore generally close to the 2-Wasserstein distance 
\citep{nguyen2021mean, ye2024distributionally}. Therefore, we believe our use of the Gelbrich formula as an approximation formula for the true 2-Wasserstein distance is reasonable.

This provides a computationally tractable and well-justified measure of intervention size. 
% If we assume the natural exposure distribution is multivariate normal, $f \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$, then our tilted distribution $g_{\boldsymbol{\delta}}$ is also normal with a shifted mean $\boldsymbol{\mu} + \boldsymbol{\Sigma}\boldsymbol{\delta}$ and the same covariance matrix $\boldsymbol{\Sigma}$. In this case, the Gelbrich formula is exact. The trace term simplifies to zero since the covariance matrices are identical:
% \begin{align*}
%     d_W^2(f, g_{\boldsymbol{\delta}}) &= ||\boldsymbol{\mu} - (\boldsymbol{\mu} + \boldsymbol{\Sigma}\boldsymbol{\delta})||^2 + \mathrm{tr}(\boldsymbol{\Sigma} + \boldsymbol{\Sigma} - 2(\boldsymbol{\Sigma}^{1/2}\boldsymbol{\Sigma}\boldsymbol{\Sigma}^{1/2})^{1/2}) \\
%     &= ||-\boldsymbol{\Sigma}\boldsymbol{\delta}||^2 + \mathrm{tr}(2\boldsymbol{\Sigma} - 2(\boldsymbol{\Sigma}^2)^{1/2}) \\
%     &= \boldsymbol{\delta}^\top \boldsymbol{\Sigma}^2 \boldsymbol{\delta} + \mathrm{tr}(2\boldsymbol{\Sigma} - 2\boldsymbol{\Sigma}) \\
%     &= \boldsymbol{\delta}^\top \boldsymbol{\Sigma}^2 \boldsymbol{\delta}
% \end{align*}
Accordingly, we measure intervention size through the Gelbrich formula applied to the marginal baseline and tilted laws of $\boldsymbol{W}$, and write the resulting quantity as $G(\boldsymbol{\delta})$. Comparing interventions on the level set $G(\boldsymbol{\delta}) = c^2$ puts them on a common scale. Under a multivariate normal model this coincides with the squared 2-Wasserstein distance, while in more general settings it remains a rigorous lower bound. The optimization problem thus becomes a search for the $\boldsymbol{\delta}$ that minimizes $\psi(\boldsymbol{\delta})$ among all possible intervention directions of a comparable size, allowing us to disentangle the direction of an intervention from its size and enabling a principled exploration of which changes to an environmental exposure mixture are most beneficial or harmful.

\subsection{Choice of Estimand}

Having established a principled method for comparing interventions of equivalent magnitude, we are now positioned to define our estimands of interest. The framework of incremental effects, when extended to a multivariate setting, moves beyond simply estimating the effect of a single, pre-specified shift or simply examining how the causal effect depends on shift size. Instead, it allows us to explore the entire space of potential interventions to identify those that are most impactful.

\subsubsection{Optimal Shifts}

In environmental contexts, a key objective is to determine the most effective strategy for intervention given limited resources. For instance, how should regulators modify a complex mixture of air pollutants to achieve the greatest improvement in health outcomes? Our framework directly addresses this question by defining an estimand for the optimal policy shift. We define our primary estimand of interest, $\boldsymbol{\delta}^*_c$, as the intervention direction that minimizes the causal effect $\psi(\boldsymbol{\delta})$ over the set of all ``fair shifts'' of a given size $c$:
$$
\boldsymbol{\delta}^*_c = \arg\min_{\boldsymbol{\delta} \in \mathcal{A}_c} \psi(\boldsymbol{\delta})
$$
where
$$
\mathcal{A}_c = \{ \boldsymbol{\delta} : G(\boldsymbol{\delta}) = c^2 \}.
$$
The corresponding value of this optimal policy is $\psi^*_c = \psi(\boldsymbol{\delta}^*_c)$. To provide some intuition for the optimal $\boldsymbol{\delta}$, we can explore it analytically in a simplified setting. If we assume the outcome model is linear ($\mu(\boldsymbol{x},\boldsymbol{w}) = \boldsymbol{\alpha}^\top \boldsymbol{x} + \boldsymbol{\beta}^\top \boldsymbol{w}$) and the exposure distribution is normal ($f \sim \mathcal{N}(\boldsymbol{\mu_x}, \boldsymbol{\Sigma})$), the causal effect is minimized when $\boldsymbol{\delta}$ is proportional to $-\boldsymbol{\Sigma}^{-1}\boldsymbol{\beta}$. This result provides some intuition: the optimal direction is a balance between the direct effect of each pollutant on the outcome (the vector $\boldsymbol{\beta}$) and the correlation structure of the mixture (represented by $\boldsymbol{\Sigma}^{-1}$). This highlights a key insight of our multivariate approach: the covariance of the exposures is critical for determining not only which shifts are easiest to estimate, but also which shifts are most impactful. While the optimal policy shift is one primary goal, our framework is flexible and allows for the definition of other estimands that can be useful in answering other scientific questions of interest in environmental epidemiology. We now detail these in the following sections.

\subsubsection{Single Exposure Shifts}

A common goal in the analysis of environmental mixtures is to identify the components of the mixture that are most harmful. This has led to a wide range of statistical approaches aimed at performing exposure selection \citep{bobb2015causal, antonelli2020estimating, ferrari2020identifying, wei2020sparse, samanta2022estimation}. These approaches have inherently disregarded the potential impacts of positivity violations when examining which exposures are most harmful, but we can adapt our approach here to target similar questions without the need for strong positivity assumptions. A natural choice is to let $\boldsymbol{\delta}$ be a vector of zeros with a single non-zero component, e.g., $\boldsymbol{\delta}_j = (0, \dots, t_j, \dots, 0)$. The magnitude $t_j$ would be chosen to satisfy the same fairness constraint, $G(\boldsymbol{\delta}_j) = c^2$. While this estimand would encourage the $j^{th}$ component of the exposures to increase more than others, in the presence of correlated exposures, it will also shift the remaining exposures, and the extent to which this occurs is less clear. A distinct approach is to define a value of $\boldsymbol{\delta}$ such that the means of the exposures in the tilted distribution are the same, except for the $j^{th}$ exposure, thereby isolating the impact of that single exposure. If the exposures follow a multivariate normal distribution, this is straightforward since the mean shift is given by $\boldsymbol{\Sigma} \boldsymbol{\delta}$. If we want to ensure that only the $j^{th}$ exposure's mean is shifted, then we could set $\boldsymbol{\delta}_j = \boldsymbol{\Sigma}^{-1} \boldsymbol{e}_j$ where $\boldsymbol{e}_j = (0, \dots, t_j, \dots, 0)$ and again $t_j$ is chosen to ensure a fair shift. Note that this analytical form only holds when the exposure follows a multivariate normal distribution, which won't be true in general. We can instead use this value of $\boldsymbol{\delta}_j$ as a starting point in a numerical algorithm that searches for the exponential tilt that only shifts the $j^{th}$ component. 

Once these are obtained, we can calculate $\psi(\boldsymbol{\delta}_j)$ for all $j = 1, \dots, q$ to infer which exposures have the biggest effect on the outcome. Further note that this approach can be naturally extended to explore interactions or combined effects. For example, by setting two components of $\boldsymbol{\delta}$ to be non-zero, one could investigate whether simultaneously increasing two pollutants has a synergistic effect greater than the sum of their individual impacts. We point readers to recent work examining stochastic interventions to identify interactions, as similar ideas could be applied within our framework, though we focus here on single exposure effects for now \citep{mccoy2023semiparametric}.

\subsubsection{Efficient Exposure Shifts}

While the previous two estimands are arguably the most scientifically and policy-relevant in most applications, there are other considerations at play, such as how efficiently we can estimate the chosen estimand. Environmental applications in particular are known to have relatively small effect sizes, and therefore efficiency can be particularly important when sample sizes are not exceedingly large. As we established in Section 2.3, the statistical difficulty of estimating $\psi(\boldsymbol{\delta})$ is heavily driven by the variance of the density ratio, $\mathrm{Var}(g_{\boldsymbol{\delta}}/f)$. For a fixed intervention size, as defined by the Wasserstein distance, we showed that the most efficient intervention direction, in terms of minimizing this variance, is proportional to the first eigenvector of the exposure covariance matrix, $\boldsymbol{\Sigma}$. We call this direction $\boldsymbol{\delta}_{\text{eff}}$, and it is clear that this direction depends only on the correlation structure of the observed exposures. While this direction is only the most efficient one under normality of the exposures, we proceed with this choice in general, as we have found that it leads to efficient estimates in more general settings, and deriving the most efficient direction in general is a difficult task. 

However, the optimal policy direction, $\boldsymbol{\delta}^*_c$, which maximizes the causal effect $\psi(\boldsymbol{\delta})$, depends on both the exposure distribution and the exposure-outcome relationship, $\mu(\boldsymbol{x},\boldsymbol{w})$. In simplified linear models, the direction of steepest ascent for the causal effect is proportional to $\boldsymbol{\Sigma}^{-1}\boldsymbol{\beta}$. In general, there is no reason for the direction of maximal statistical efficiency (related to the eigenvectors of $\boldsymbol{\Sigma}$) to be the same as the direction of the maximal causal effect (related to $\boldsymbol{\Sigma}^{-1}\boldsymbol{\beta}$). To see this, consider an intuitive example with two highly and positively correlated pollutants, where the first principal component is approximately in the $(1, 1)$ direction, which corresponds to the direction that is ``easiest" to estimate with the observed data. Now, suppose that only the second pollutant has a strong causal effect on the outcome (i.e., $\boldsymbol{\beta} \approx (0, \beta_2)$). The optimal policy would primarily involve shifting the second pollutant. Our framework reveals an inherent tension: the policy we most want to evaluate (shifting the second pollutant alone) is statistically difficult because it moves in a direction against the data's strong correlation structure, leading to a high-variance density ratio and thus high uncertainty in our estimate of its effect. In general, this presents a trade-off between interpretability and statistical efficiency, and users can decide based on features of their observed data which estimand to target. 

% \subsection{Conditional Stochastic Interventions}

% While the single exposure shifts described above attempt to isolate the effect of component $j$ by fixing the means of other components, this mean-shift based approach has fundamental limitations in identifying single-pollutant effects. While this approach guarantees that only the mean of exposure $j$ shifts, while the other exposures have their means fixed, it is not clear what happens to the full distributions of the exposures. It is possible for the mean to remain constant, but for other aspects of the distribution to shift substantially, which can have unintended effects and make the interpretation of these estimands less clear. 

% To resolve this issue and guarantee that the intervention corresponds to only changing exposure $j$, we propose a conditional stochastic intervention. Instead of tilting the joint distribution based on mean constraints, we modify the conditional distribution of $W_j$ while leaving the distribution of all other pollutants $W_{-j}$ unchanged. We define the intervention density $g_{\delta_j}^{(j)}$ by tilting the baseline conditional density of $W_j$ given covariates and other pollutants:
% $$
% g_{\delta_j}^{(j)}(x, w_j, w_{-j}) = f(x, w_{-j}) g_j(w_j | x, w_{-j}; \delta_j)
% $$
% where $g_j(w_j|x,w_{-j};\delta_j) \propto \exp(\delta_j w_j) f_j(w_j|x,w_{-j})$ for a tilt parameter $\delta_j \ge 0$. Importantly, this construction has three key properties: 1) the joint distribution of $(X, W_{-j})$ under $g_{\delta_j}^{(j)}$ is identical to that under $f$, 2) positivity is still preserved, and 3) the conditional distribution of $W_j$ under $g_{\delta_j}^{(j)}$ is stochastically larger than under $f$ at every configuration of $(x, w_{-j})$ in the sense that $P_{g_{\delta_j}^{(j)}}(W_j \le t \mid X=x, W_{-j}=w_{-j}) \le P_f(W_j \le t \mid X=x, W_{-j}=w_{-j})$ for all $t \in \mathbb{R}$. These properties ensure that this estimand corresponds to increasing only exposure $j$ and therefore can be used to compare exposures and identify which ones are most harmful. 

\section{Estimation and Inference}
\label{sec:estimation}

\subsection{Estimating $\psi(\boldsymbol{\delta})$}

For a fixed intervention vector $\boldsymbol{\delta}$, the target estimand is the expected outcome under the tilted exposure distribution:
$$
\psi(\boldsymbol{\delta}) = \mathbb{E}\left[\int_{\mathcal{W}} \mu(\boldsymbol{X}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w}\right]
$$
where the outer expectation is over the marginal distribution of covariates $\boldsymbol{X}$. Therefore, a direct approach to estimating $\psi(\boldsymbol{\delta})$ is through a plug-in procedure. This method involves replacing each component in the expression above with a corresponding empirical estimate, which leads to the plug-in estimator:
$$
\hat{\psi}_{\text{plugin}}(\boldsymbol{\delta}) = \frac{1}{n} \sum_{i=1}^{n} \left[ \int_{\mathcal{W}} \hat{\mu}(\boldsymbol{X}_i, \boldsymbol{w}) \hat{g}_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}_i) \, d\boldsymbol{w} \right]
$$

However, this estimator faces certain practical and theoretical challenges. One issue is that the estimator's performance is highly dependent on an accurate estimate of the multivariate conditional density $\hat{f}(\boldsymbol{w}|\boldsymbol{x})$, which can be difficult to estimate for multivariate exposures, and will likely have slower convergence rates. Furthermore, this approach does not leverage the structure of the efficient influence function and, as a result, is generally not statistically efficient. These limitations motivate alternative estimators with superior statistical properties.

\subsubsection{One-step Estimation and Cross-fitting}

To overcome the limitations of the plug-in estimator, we employ an approach rooted in semiparametric efficiency theory. This method uses the efficient influence function (EIF) to construct an estimator that is consistent under weaker conditions and achieves the optimal asymptotic variance. The EIF for the estimand $\psi(\boldsymbol{\delta})$ is given in Section \ref{sec:Estimands} by $\varphi(\boldsymbol{Z}; \boldsymbol{\delta}) = D_Y + D_{g,\mu} + D_{\psi}$. In our notation, substituting the EIF components and algebraically combining the first two terms yields
$$
\varphi(\boldsymbol{Z}; \psi, \mu, f)
= r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\Big\{Y-\mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]\Big\}
+ \mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}] - \psi,
$$
where $r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x}) = g_{\boldsymbol{\delta}}(\boldsymbol{w}\mid \boldsymbol{x})/f(\boldsymbol{w}\mid \boldsymbol{x})$ and expectations with subscript $g_{\boldsymbol{\delta}}$ are taken with respect to $g_{\boldsymbol{\delta}}(\cdot\mid \boldsymbol{X})$. The one-step estimation procedure utilizes this EIF to correct an initial parameter estimate by adding the empirical average of the EIF to the initial plug-in estimate, which serves as a bias-correction term:
$$
\hat{\psi}_{\text{onestep}}(\boldsymbol{\delta})
= \tilde{\psi}_{\text{plugin}}(\boldsymbol{\delta})
+ \frac{1}{n} \sum_{i=1}^{n}
\varphi\!\big(\boldsymbol{Z}_i; \tilde{\psi}_{\text{plugin}}, \hat{\mu}, \hat{f}\big).
$$
This can be re-written to show that the one-step estimator takes the following form:
$$
\begin{aligned}
\hat{\psi}_{\text{onestep}}(\boldsymbol{\delta})
= \frac{1}{n}\sum_{i=1}^n
\hat r(\boldsymbol{W}_i,\boldsymbol{X}_i)\big[Y_i-\mathbb{E}_{\hat g_{\boldsymbol{\delta}}}[\hat\mu\mid \boldsymbol{X}_i]\big]
+ \frac{1}{n}\sum_{i=1}^n \mathbb{E}_{\hat g_{\boldsymbol{\delta}}}[\hat\mu\mid \boldsymbol{X}_i].
\end{aligned}
$$
This estimator has a number of key features that we will describe in subsequent sections when we study the asymptotic properties of this estimator. To summarize, it allows the use of flexible machine learning methods for estimation of each of the nuisance functions, and it is asymptotically efficient given its construction based on the EIF. The practical performance of the estimator is highly dependent on an estimate of the conditional density of the exposures, given by $f$, which can be challenging with a moderate number of exposures. This density shows up in the expectations with respect to $g_{\boldsymbol{\delta}}$, but also in the ratio term, denoted by $r_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})$. First, we detail how to estimate this quantity directly using estimates of $f$ and $\mu$, though in Section \ref{sssec:ClassificationDensity} we propose an approach to directly estimating this quantity using regression techniques that may not have the same theoretical properties, but can have good finite-sample performance when there are a moderate number of exposures. 

%Second, the estimator is Neyman orthogonal, i.e.\ at the nuisance true value $\eta_0=\left(\mu_0, r_0\right)$ we have $\left.\partial_\eta \mathbb{E}[m(Z ; \eta)]\right|_{\eta=\eta_0}=0$. 

To ensure the desirable asymptotic properties of our final estimator for $\psi(\boldsymbol{\delta})$, the entire estimation procedure is embedded within a cross-fitting framework. Cross-fitting is a technique designed to eliminate a key source of bias that arises when the same data is used both to train nuisance parameters and to evaluate the final parameter of interest. This prevents overfitting inherent in data-adaptive methods \citep{zheng2011cross, chernozhukov2018double} and has been shown to improve performance for related EIF based estimators. The procedure is implemented as follows. The data is randomly partitioned into $K$ disjoint folds of approximately equal size. For each fold $k \in \{1, \dots, K\}$, we treat it as the evaluation set and use the remaining $K-1$ folds as the training set. On the training set, we fit our nuisance models, including the outcome regression $\hat{\mu}_{-k}(\boldsymbol{x},\boldsymbol{w})$ and the exposure density $\hat{f}_{-k}(\boldsymbol{w},\boldsymbol{x})$. These models, trained on data not in fold $k$, are then used to compute the components of the efficient influence function for every observation $i$ only within the evaluation fold $k$. The final estimate, $\hat{\psi}(\boldsymbol{\delta})$, is then constructed by solving the estimating equation aggregated across all $K$ folds, ensuring that the nuisance function estimates for any given observation are always independent of that observation itself. This approach to nuisance function estimation has theoretical advantages by allowing for less restrictive assumptions on the nuisance functions, and important finite-sample properties as it tends to reduce bias in the estimated causal effects that is induced from overfitting. 

% \paragraph{Estimating Equations and its Equivalency to One-step Estimator in our Setup}

% Estimating equations derived from the EIF provide an alternative method for constructing a rate robust and efficient estimator. This approach is based on the mean zero property of EIF, $\mathbb{E}[\varphi(\boldsymbol{Z}; \psi, \boldsymbol{\eta})] = 0$, where $\boldsymbol{\eta}$ represents the nuisance functions. The estimator for $\psi(\boldsymbol{\delta})$ is the solution to the empirical version of this moment condition.

% Similar to the one-step estimator, the procedure first requires estimates of the nuisance functions, $\hat{\mu}(\boldsymbol{x},\boldsymbol{w})$ and $\hat{r}(\boldsymbol{w},\boldsymbol{x})$. Given the nuisance estimates $\hat{\boldsymbol{\eta}} = \{\hat{\mu}, \hat{r}\}$, the estimating equation for $\psi$ is:
% $$
% \frac{1}{n} \sum_{i=1}^{n} \varphi(\boldsymbol{Z}_i; \psi, \hat{\boldsymbol{\eta}}) = 0
% $$
% The estimator, $\hat{\psi}_{\text{EE}}$, is the solution to this equation. For many complex EIFs, solving this equation may require iterative numerical methods. However, because the EIF is linear in $\psi$ in this setting, the equation has a closed-form solution.

% Expanding the estimating equation with the EIF components yields:

% $$
% \frac{1}{n} \sum_{i=1}^{n} \left[ D_Y(\boldsymbol{Z}_i; \hat{\boldsymbol{\eta}}) + D_{g,\mu}(\boldsymbol{Z}_i; \hat{\boldsymbol{\eta}}) + D_{\psi}(\boldsymbol{Z}_i; \psi, \hat{\boldsymbol{\eta}}) \right] = 0
% $$
% $$
% \frac{1}{n} \sum_{i=1}^{n} \left[ \hat{r}(\boldsymbol{W}_i,\boldsymbol{X}_i)(Y_i - \hat{\mu}(\boldsymbol{X}_i,\boldsymbol{W}_i)) + \hat{r}(\boldsymbol{W}_i,\boldsymbol{X}_i)(\hat{\mu}(\boldsymbol{X}_i,\boldsymbol{W}_i) - \mathbb{E}_{\hat{g}_{\boldsymbol{\delta}}}[\hat{\mu}|\boldsymbol{X}_i]) + (\mathbb{E}_{\hat{g}_{\boldsymbol{\delta}}}[\hat{\mu}|\boldsymbol{X}_i] - \psi) \right] = 0
% $$
% We can now solve for $\psi$:
% \begin{align*}
% \psi_{EE} &= \frac{1}{n} \sum_{i=1}^{n} \left[ \hat{r}(\boldsymbol{W}_i,\boldsymbol{X}_i)(Y_i - \hat{\mu}(\boldsymbol{X}_i,\boldsymbol{W}_i)) + \hat{r}(\boldsymbol{W}_i,\boldsymbol{X}_i)(\hat{\mu}(\boldsymbol{X}_i,\boldsymbol{W}_i) - \mathbb{E}_{\hat{g}_{\boldsymbol{\delta}}}[\hat{\mu}|\boldsymbol{X}_i]) + \mathbb{E}_{\hat{g}_{\boldsymbol{\delta}}}[\hat{\mu}|\boldsymbol{X}_i] \right] \\
% &= \frac{1}{n} \sum_{i=1}^{n} \mathbb{E}_{\hat{g}_{\boldsymbol{\delta}}}[\hat{\mu}|\boldsymbol{X}_i] + \frac{1}{n} \sum_{i=1}^{n} \hat{r}(\boldsymbol{W}_i,\boldsymbol{X}_i)(Y_i - \mathbb{E}_{\hat{g}_{\boldsymbol{\delta}}}[\hat{\mu}|\boldsymbol{X}_i])
% \end{align*}



% The first term is the initial plug-in estimator $\tilde{\psi}(\boldsymbol{\delta})$, also note $\frac{1}{n} \sum_i\left(\mathbb{E}_{\hat{g}_{\boldsymbol{\delta}}}\left[\hat{\mu} \mid \boldsymbol{X}_i\right]-\tilde{\psi}_{\text {plugin }}\right)=0$, making this solution algebraically identical to the one-step estimator. Here the linearity of the EIF in $\psi$ is advantageous because it yields a non-iterative, closed-form solution. The cancellation of the term $\tilde{\psi}$ also ensuring the final estimator is Neyman Orthogonal and asymptotically efficient regardless of the convergence of the initial estimate $\tilde{\psi}$.

\subsubsection{Direct estimation using regression approaches}
\label{sssec:ClassificationDensity}

When there are a moderate number of exposures, estimation of $\psi(\boldsymbol{\delta})$ becomes increasingly challenging, even for the efficient one-step estimators described above due to the inherent difficulty of estimating a multivariate, conditional distribution $f(\boldsymbol{w} \mid \boldsymbol{x})$. For this reason we also explore an approach, first described in \cite{schindl2024incremental}, that does not require estimation of the exposure density at all. This can be advantageous in finite samples, particularly when estimation of the density ratio $r_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})$ is unstable. The first key insight is that the density ratio can be written as
$$r_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X}) = \frac{\text{exp}(\boldsymbol{\delta}^\top \boldsymbol{w})}{{\int_{\mathcal{W}} \exp(\boldsymbol{\delta}^\top \boldsymbol{v}) f(\boldsymbol{v} \mid \boldsymbol{x}) \, d\boldsymbol{v}}} = \frac{\text{exp}(\boldsymbol{\delta}^\top \boldsymbol{w})}{\mathbb{E}[ \exp(\boldsymbol{\delta}^\top \boldsymbol{W}) \mid \boldsymbol{X}]} = \frac{\text{exp}(\boldsymbol{\delta}^\top \boldsymbol{w})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{X})},$$
which shows the density ratio can be estimated by estimating the conditional expectation $\nu_{\boldsymbol{\delta}}(\boldsymbol{X})$. This does not require the conditional density of the exposures and can be carried out using flexible, univariate regression techniques. Further, the other key component of our one-step estimator can be written as
{\small
$$\int_{\mathcal{W}} \mu(\boldsymbol{X}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} = \frac{\int_{\mathcal{W}} \mu(\boldsymbol{X}, \boldsymbol{w}) \exp(\boldsymbol{\delta}^\top \boldsymbol{w}) f(\boldsymbol{w} \mid \boldsymbol{x}) \, d\boldsymbol{w}}{\int_{\mathcal{W}} \exp(\boldsymbol{\delta}^\top \boldsymbol{v}) f(\boldsymbol{v} \mid \boldsymbol{x}) \, d\boldsymbol{v}} = \frac{\mathbb{E}[ \exp(\boldsymbol{\delta}^\top \boldsymbol{W}) \mu(\boldsymbol{X}, \boldsymbol{W}) \mid \boldsymbol{X}]}{\nu_{\boldsymbol{\delta}}(\boldsymbol{X})} = \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{X})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{X})}.$$
}
This shows that this quantity can be estimated by taking the ratio of two quantities, each of which can be estimated using flexible, univariate regression techniques. This was introduced in \cite{schindl2024incremental}, though they did not implement this estimator as they found it to be unstable by taking the ratio of the estimates for these two conditional expectations. They were working, however, in the univariate exposure setting where estimating the conditional density of the exposures is more straightforward. In our setting, with multiple exposures, conditional density estimation can be very difficult, whereas this approach relies on univariate prediction models only. Additionally note, that one can take a third strategy, which is to still estimate the conditional density of the exposures and use it whenever calculating $\int_{\mathcal{W}} \mu(\boldsymbol{X}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w}$, but then use the regression approach described above for estimating the density ratio to improve stability of our estimates. While potentially useful for estimation, these estimators that obviate the need to estimate the exposure density will not inherit the same theoretical properties as the one-step estimator that directly uses estimates of $f$ and $\mu$, which we study theoretically in Section \ref{sec:Theory}. They may, however, produce better finite sample performance, which we study in the simulation studies in Section~\ref{sec:Simulations} across a wide range of exposure distributions. 
% {\color{blue} We should replace this section with the approaches that are based on regression. }

% While estimation can proceed directly with estimates of both $f$ and $\mu$, the density ratio
% $r(\boldsymbol{w},\boldsymbol{x}) = g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x}) / f(\boldsymbol{w} \mid \boldsymbol{x})$ can be unstable when there is misspecification of the exposure density $f$. While we necessarily must estimate this density $f$ for calculation of terms involving $g_w$, it is not necessary for estimation of this potentially unstable density ratio. To see this, we now show how this task can be posed as a classification problem, which allows for a direct and more stable estimation of the ratio itself \citep{diaz2023nonparametric}.

% The procedure involves constructing an augmented dataset of size $2n$. Each original observation $(\boldsymbol{X}_i, \boldsymbol{W}_i)$ generates two records: $(\boldsymbol{X}_i, \boldsymbol{W}_i)$ with a class label $\lambda_i=0$, and $(\boldsymbol{X}_i, \boldsymbol{W}_i^{\boldsymbol{\delta}})$ with a label $\lambda_i=1$, where $\boldsymbol{W}_i^{\boldsymbol{\delta}}$ is a sample drawn from the target distribution $g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}_i)$. This sample can be generated via importance resampling from the observed exposures $\{\boldsymbol{W}_j\}_{j=1}^n$ conditional on $\boldsymbol{X}_i$, for example, by selecting observations with $\boldsymbol{X}_j$ similar to $\boldsymbol{X}_i$ (e.g., using a kernel or nearest neighbors) and then resampling with weights proportional to $\exp(\boldsymbol{\delta}^\top \boldsymbol{W}_j)$. The resulting data point is $(\boldsymbol{X}_i, \boldsymbol{W}_i^{\delta}, \lambda_i=1)$. We then train a flexible classifier on this dataset to estimate the conditional probability $\hat{u}(\boldsymbol{x},\boldsymbol{w}) = P(\lambda=1 \mid \boldsymbol{X}=\boldsymbol{x}, \boldsymbol{W}=\boldsymbol{w})$.

% The density ratio is linked to this probability via Bayes' rule. Given our balanced construction where $P(\lambda=1)=P(\lambda=0)=1/2$, the relationship simplifies significantly:
% $$
% r(\boldsymbol{w},\boldsymbol{x}) = \frac{g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x})}{f(\boldsymbol{w} \mid \boldsymbol{x})} = \frac{P(\lambda=1 \mid \boldsymbol{W}=\boldsymbol{w}, \boldsymbol{X}=\boldsymbol{x}) / P(\lambda=1)}{P(\lambda=0 \mid \boldsymbol{W}=\boldsymbol{w}, \boldsymbol{X}=\boldsymbol{x}) / P(\lambda=0)} = \frac{u(\boldsymbol{x},\boldsymbol{w})}{1-u(\boldsymbol{x},\boldsymbol{w})}
% $$
% Thus, the ratio is estimated as $\hat{r}(\boldsymbol{w},\boldsymbol{x}) = \hat{u}(\boldsymbol{x},\boldsymbol{w}) / (1-\hat{u}(\boldsymbol{x},\boldsymbol{w}))$, transforming a difficult density estimation problem into a more tractable classification task.

\subsection{Optimizing over a Manifold}

Our primary estimand, the optimal policy shift $\boldsymbol{\delta}^*_c$, is defined as the solution to
$$
\min_{\boldsymbol{\delta}\in\mathcal{M}} \psi(\boldsymbol{\delta}),
$$
where $\mathcal{M} := \{\boldsymbol{\delta}\in\mathbb{R}^d : G(\boldsymbol{\delta}) = c^2\}$ and $G$ is the Gelbrich quantity defined in Section 2.4. We assume $c^2$ is a regular value of $G$ (equivalently, $\nabla G(\boldsymbol{\delta})\neq \boldsymbol{0}$ for all $\boldsymbol{\delta}\in\mathcal{M}$), so that $\mathcal{M}$ is a smooth embedded hypersurface. This regularity holds generically and is verified for the Gelbrich constraint in Appendix B. Standard Euclidean optimization algorithms such as gradient descent are not directly applicable as a gradient step taken from a point on the manifold will likely lead to a point outside of the feasible set.

To properly solve this problem, we must recognize that the constraint set forms a smooth, curved space known as a Riemannian manifold. Optimization on manifolds requires specialized techniques that generalize concepts from Euclidean optimization. The core idea is to perform optimization steps within the tangent space at each point on the manifold, which is a local linear approximation of the manifold, and then map the result back onto the manifold itself. For our specific constrained problem, we employ a Riemannian Broyden Fletcher Goldfarb Shanno (BFGS) algorithm. This is a powerful quasi-Newton method adapted for optimization on manifolds, which generally offers faster convergence than simpler first-order methods. In practice, the method is implemented with two computationally light ingredients: a projection-based retraction back to the level set, and an inexpensive projection-based vector transport between tangent spaces. The key components of this algorithm for our problem are: 

\begin{enumerate}
    \item Preliminary definitions: A definition of the tangent space is to take any small smooth curve on $\mathcal{M}$
    $$
    \gamma:(-\varepsilon, \varepsilon) \rightarrow \mathcal{M}, \quad \gamma(0)=\boldsymbol{\delta}.
    $$
    Then
    $$
    \gamma^{\prime}(0) \in \mathbb{R}^d,
    $$
    is a valid tangent vector. The tangent space at a point $\boldsymbol{\delta}$ is the collection of all such vectors:
    $$
    T_\delta \mathcal{M}=\left\{\gamma^{\prime}(0): \gamma(0)=\delta, \gamma(t) \in \mathcal{M} \text { for all } t\right\}
    $$
    For a level set $\mathcal{M}=\{\boldsymbol{\delta}:G(\boldsymbol{\delta})=c^2\}$, we also have the equivalent characterization
    $T_{\boldsymbol{\delta}}\mathcal{M}=\text{Null}(\nabla G(\boldsymbol{\delta})^\top)$.
    The BFGS (Broyden–Fletcher–Goldfarb–Shanno) algorithm is a highly effective quasi-Newton method, which finds an optimum by maintaining and iteratively updating an approximation $\mathbf{B}$ of the inverse Hessian matrix. In Euclidean space $\mathbb{R}^n$, the standard update formula is:
    $$
    \mathbf{B}_{k+1} = \mathbf{B}_k + \frac{\mathbf{b}_k \mathbf{b}_k^\top}{\mathbf{b}_k^\top \mathbf{a}_k} - \frac{(\mathbf{B}_k \mathbf{a}_k) (\mathbf{B}_k \mathbf{a}_k)^\top}{\mathbf{a}_k^\top \mathbf{B}_k \mathbf{a}_k}
    $$
    Where:
    \begin{itemize}
        \item $\mathbf{B}_{k+1}$ is the updated approximation of the inverse Hessian, which is the target of the update.
        \item $\mathbf{B}_k$ is the current approximation of the inverse Hessian.
        \item $\mathbf{a}_k$ is the change in position (step), defined as $\mathbf{a}_k = \boldsymbol{\delta}_{k+1} - \boldsymbol{\delta}_k$.
        \item $\mathbf{b}_k$ is the change in gradient, defined as $\mathbf{b}_k = \nabla\psi(\boldsymbol{\delta}_{k+1}) - \nabla\psi(\boldsymbol{\delta}_k)$
    \end{itemize}

    \item Riemannian Gradient: The standard (Euclidean) gradient, $\nabla \psi(\boldsymbol{\delta})$, must be projected onto the tangent space at the current point $\boldsymbol{\delta}$ to find the direction of steepest ascent along the manifold. Let $\nabla G(\boldsymbol{\delta})$ denote the Euclidean normal to the level set at $\boldsymbol{\delta}$, and let $\boldsymbol{n}(\boldsymbol{\delta}) = \nabla G(\boldsymbol{\delta}) / \|\nabla G(\boldsymbol{\delta})\|$ be the corresponding unit normal vector. The orthogonal projection matrix onto the tangent space is defined as $P_{\boldsymbol{\delta}} := I - \boldsymbol{n}(\boldsymbol{\delta})\boldsymbol{n}(\boldsymbol{\delta})^\top$. Consequently, the Riemannian gradient under the induced Euclidean metric is given by
    $$    \operatorname{grad}\psi(\boldsymbol{\delta}) = P_{\boldsymbol{\delta}} \nabla \psi(\boldsymbol{\delta}).
    $$


    \item Retraction: Even though we are moving based on a Riemannian gradient step that is in the current point's tangent space (which is essentially a linear approximation of the manifold at the current point), we are still technically moving out of the manifold. After finding a search direction $\boldsymbol{v}$, we need a retraction to map the point from the tangent space back onto the manifold. For the level-set manifold $\mathcal{M}$, we take the projection retraction $R_{\boldsymbol{\delta}}(\boldsymbol{\xi})=\Pi(\boldsymbol{\delta}+\boldsymbol{\xi})$, where $\Pi$ is the orthogonal projection onto $\mathcal{M}$, which is a canonical construction for embedded manifolds. In our code, $\Pi$ is computed approximately by a single normal-direction correction, which can be interpreted as a projection-like update that preserves the local first-order accuracy required of a retraction while substantially reducing computational cost.

    \item Vector Transport: Vector transport is required to compare tangent vectors that live in different tangent spaces across iterates. For our embedded level-set manifold, we use the simple projection transport:
    $$
    \widetilde{\mathcal{T}}_{\boldsymbol{\delta}\to \boldsymbol{\delta}_+}(\boldsymbol{\zeta}) := P_{\boldsymbol{\delta}_+}\boldsymbol{\zeta},
    $$
    namely, orthogonally projecting an ambient vector onto the new tangent space. Such a transport is generally not an isometry, even though it is often computationally attractive. This transport is also used to move tangent-space quantities between iterates when forming the RBFGS update.
\end{enumerate}
To summarize, the iterative process of the Riemannian BFGS algorithm is outlined as follows.

\begin{algorithm}[H]
\caption{Riemannian BFGS for Optimal Policy Shift}
\label{alg:rbfgs}
\begin{algorithmic} % Add [1] for line numbering
\State Initialize: $k=0$, choose $\boldsymbol{\delta}_0$ on the manifold (s.t. $G(\boldsymbol{\delta}_0)=c^2$).
\State Compute Euclidean gradient $\nabla\psi(\boldsymbol{\delta}_0)$ and Riemannian gradient $\operatorname{grad}\psi(\boldsymbol{\delta}_0)=P_{\boldsymbol{\delta}_0}\nabla\psi(\boldsymbol{\delta}_0)$.
\State Initialize inverse Hessian approximation $\boldsymbol{B}_0 = \boldsymbol{I}$.

\While{not converged (e.g., $\|\operatorname{grad}\psi(\boldsymbol{\delta}_k)\| > \epsilon$)}
  \State Compute search direction: $\boldsymbol{p}_k = -\boldsymbol{B}_k \operatorname{grad}\psi(\boldsymbol{\delta}_k)$.
  \State Perform a weak Wolfe line search along the retraction curve.
  \State Update point via retraction: $\boldsymbol{\delta}_{k+1} = R_{\boldsymbol{\delta}_k}(\alpha_k \boldsymbol{p}_k)$.
  \State Compute new Riemannian gradient $\operatorname{grad}\psi(\boldsymbol{\delta}_{k+1})$.
  \State Update $\boldsymbol{B}_{k+1}$: apply the RBFGS update and transport $\boldsymbol{B}_k$ to the new tangent space as needed.
  \State $k \leftarrow k+1$.
\EndWhile
\State \Return{$\boldsymbol{\delta}_k$}
\end{algorithmic}
\end{algorithm}

When the objective is to minimize $\psi(\boldsymbol{\delta})$ over the Gelbrich level set, convergence guarantees for RBFGS depend on the line-search conditions, the regularity of the objective along retraction curves, and the choice of vector transport. Under the assumptions stated in Appendix B, the global convergence result in Theorem 4.2 of \citet{huang2018riemannian} yields $\liminf_{k\to\infty}\|\operatorname{grad}\psi(\boldsymbol{\delta}_k)\|=0$ for the RBFGS scheme equipped with a suitable isometric vector transport and weak Wolfe line search.
Appendix B verifies the geometric regularity of the Gelbrich level set, establishes objective regularity along the retraction curve, and invokes the existence of a weak Wolfe step. The proof therefore uses a fully rigorous projection retraction and the scaled isometric vector transport $\mathcal{T}^S$ \citep{huang2015broyden} together with an explicit boundary condition on $G$ that yields compactness of the relevant level set. Generally, however, these stricter choices are made for the convergence proof. In the actual implementation we use a computationally cheaper projection-type retraction and the orthogonal projection transport $\widetilde{\mathcal{T}}$, together with safeguard checks on the RBFGS update. This separation between the proof device and the working algorithm is standard in large-scale Riemannian optimization \citep{ring2012optimization,huang2018riemannian}. In our numerical work, the simplified implementation converged stably to a local solution while substantially reducing computation time.


In embedded-manifold settings, the projection transport $\boldsymbol{\zeta}\mapsto P_{\boldsymbol{\delta}_+}\boldsymbol{\zeta}$ can significantly reduce computational time without degrading practical convergence behavior. This phenomenon is well documented in the RBFGS experiments of \citet{qi2010riemannian}, where projection-based transport on the Stiefel manifold reduces wall-clock time from $304.0$ seconds to $24.0$ seconds and also decreases the iteration count from $175$ to $83$ in the Procrustes problem. Moreover, \citet{huang2018riemannian} compare combinations that satisfy sufficient conditions used in global convergence theory with cheaper combinations that do not, and find that the numbers of function and gradient evaluations (as well as vector transports) are not significantly affected by the choice of retraction and transport; as a result, lower-complexity retractions and transports can be markedly faster in terms of computational time. In our applications, the simplified implementation described above converges reliably and is computationally fast.


\section{Semiparametric Efficiency Theory}
\label{sec:Theory}

This section explores the fundamental limits of estimation for the multivariate incremental effect, $\psi(\boldsymbol{\delta})$. The analysis characterizes how the statistical difficulty of this problem depends not only on the sample size $n$, but on the intervention vector $\boldsymbol{\delta}$ and its interplay with the exposure covariance structure $\boldsymbol{\Sigma}$. We generalize and further develop the theoretical analysis for univariate continuous exposures from \citep{schindl2024incremental} to our multivariate setting. 

% To analyze the efficiency bound's structure and its dependence on the intervention, we first analyze the problem under a specific distributional model for the exposures. The joint distribution of an environmental mixture is typically complex and non-normal, often exhibiting skewness and bounded support. We hypothesize that the multivariate normal distribution serves as a mathematically tractable approximation for deriving fundamental theoretical properties. This assumption allows for the derivation of a closed-form expression for the efficiency bound, clarifying the interplay between the intervention direction $\boldsymbol{\delta}$ and the covariance structure $\boldsymbol{\Sigma}$ that is expected to hold more generally. The results from this model provide a theoretical intuition for the inherent statistical difficulty of the problem.

% \subsection{Efficiency Bound under a Normal Model}

% The variance of the efficient influence function (EIF), $\mathrm{Var}(\varphi(Z; \boldsymbol{\delta}))$, is the semiparametric efficiency bound and establishes the minimum asymptotic variance for any regular estimator. In the univariate case, this bound grows with the magnitude of the tilt parameter \citep{schindl2024incremental}. We extend this result to the multivariate case, where the bound depends on a quadratic form of the intervention vector $\boldsymbol{\delta}$ and the covariance matrix $\boldsymbol{\Sigma}$. The following lemma formalizes this relationship under a tractable distributional assumption.

% \begin{lemma}
% \label{lemma:eif_bounds_revised}
% Under the multivariate normal exposure model $W \mid X \sim \mathcal{N}(\boldsymbol{\mu}_X, \boldsymbol{\Sigma})$, and assuming bounded outcomes $|Y| \leq M$, if we decompose the EIF as $\varphi = \varphi_1 + \varphi_{\perp}$, where $\varphi_1(z) = \frac{g_{\boldsymbol{\delta}}(w|x)}{f(w|x)}(y-\mu(x,w))$, the variance of the first piece from efficient influence function $\varphi_1(z)$ satisfies:
% $$
% \mathrm{Var}(\varphi_1(Z; \boldsymbol{\delta})) = \Theta\left(\exp(\boldsymbol{\delta}^\top \boldsymbol{\Sigma} \boldsymbol{\delta}) - 1\right)
% $$
% where $\Theta(\cdot)$ denotes that the variance is of the exact asymptotic order of the term in parentheses.
% \end{lemma}

% This lemma is a crucial generalization. It demonstrates that the difficulty of estimation, as captured by the efficiency bound, is not simply a function of the norm of $\boldsymbol{\delta}$, but rather of the quadratic form $\boldsymbol{\delta}^\top \boldsymbol{\Sigma} \boldsymbol{\delta}$.


\subsection{Minimax Lower Bound}
\label{sec:minimax}

In this section, we establish a minimax lower bound for the incremental effect
$$
\theta(\boldsymbol{\delta})\ :=\ \psi(\boldsymbol{\delta})-\psi(\boldsymbol{0}),
$$
under a flexible nonparametric model. Minimax lower bounds benchmark what is
statistically achievable without imposing additional structure: they show that no
estimator can attain uniformly smaller risk over a given model class. Before presenting the main results, we must first define a number of important terms. First, we refer to the centered version of the exposures as
$$
\tilde{\boldsymbol{W}}:=\boldsymbol{W}-\E[\boldsymbol{W}\mid \boldsymbol{X}].
$$
To analyze the asymptotic variance of the effect difference $\theta(\boldsymbol{\delta})$, we decompose the problem into an incremental component $\boldsymbol{h}(\boldsymbol{Z})$ and a baseline influence function $\varphi_0(\boldsymbol{Z})$. We define
$$
\boldsymbol{h}(\boldsymbol{Z})\ :=\ \tilde{\boldsymbol{W}}\Big(Y-\E[\mu\mid \boldsymbol{X}]\Big)\;-\;\E\big[\E[\mu\tilde{\boldsymbol{W}}\mid \boldsymbol{X}]\big],
\qquad
\varphi_0(\boldsymbol{Z}):=Y-\psi(\boldsymbol{0}).
$$
Next, we calculate the covariance structure of $\boldsymbol{h}(\boldsymbol{Z})$. A key part of this variance arises from the outcome regression. To ensure this term represents a proper covariance (centered moment), we compute the raw second moment and subtract the outer product of the mean:
$$
\boldsymbol{\Sigma}_{\mu,\mathrm{full}}
:=\E\!\Big[\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top\big(\mu-\E[\mu\mid \boldsymbol{X}]\big)^2\Big]
\;-\;
\E\big[\E[\mu\tilde{\boldsymbol{W}}\mid \boldsymbol{X}]\big]\E\big[\E[\mu\tilde{\boldsymbol{W}}\mid \boldsymbol{X}]\big]^\top.
$$
Then, letting $\boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}:=\E\big[\Var(Y\mid \boldsymbol{X},\boldsymbol{W})\,\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top\big]$ be the residual variance component, we show in the appendix that we can write the full covariance matrix of $\boldsymbol{h}(\boldsymbol{Z})$ as
$$
\boldsymbol{H}\ :=\ \Cov\!\big(\boldsymbol{h}(\boldsymbol{Z})\big)
\ =\
\boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}
\ +\
\boldsymbol{\Sigma}_{\mu,\mathrm{full}}.
$$
Finally, estimating the incremental effect $\theta(\boldsymbol{\delta})$ requires distinguishing the variation in the shift direction from the variation in the baseline. Since the gradient component $\boldsymbol{h}(\boldsymbol{Z})$ and the baseline influence $\varphi_0(\boldsymbol{Z})$ are typically correlated, the fundamental difficulty of estimating their difference is governed by the variability of $\boldsymbol{h}$ that cannot be explained by $\varphi_0$. Mathematically, this corresponds to the residual variance of $\boldsymbol{h}$ after linearly projecting it onto the space spanned by $\varphi_0$, yielding the Schur--complement covariance
$$
\boldsymbol{\Gamma}\ :=\ \boldsymbol{H}\ -\ \frac{\Cov(\boldsymbol{h},\varphi_0)\,\Cov(\boldsymbol{h},\varphi_0)^{\!\top}}{\Var(\varphi_0)}\ \succeq\ \boldsymbol{0}.
$$

% Equivalently, if we set
% $$
% \beta\ :=\ \frac{\Cov(\boldsymbol{h},\varphi_0)}{\Var(\varphi_0)},\qquad
% \boldsymbol{h}_\perp\ :=\ \boldsymbol{h}-\beta\,\varphi_0,
% $$
% then $\boldsymbol{\Gamma}=\Cov(\boldsymbol{h}_\perp)$ is precisely the covariance of the residual obtained by linearly projecting $\boldsymbol{h}$ onto the one-dimensional span of $\varphi_0$. In particular, for any vector $\boldsymbol{\delta}$,
% $$
% \boldsymbol{\delta}^\top\boldsymbol{\Gamma}\,\boldsymbol{\delta}
% \ =\
% \Var\!\big(\boldsymbol{\delta}^\top\boldsymbol{h}\big)\;-\;\frac{\Cov\!\big(\boldsymbol{\delta}^\top\boldsymbol{h},\varphi_0\big)^2}{\Var(\varphi_0)}
% \ \ge\ 0,
% $$
% so $\boldsymbol{\Gamma}$ captures the variance of $\boldsymbol{\delta}^\top\boldsymbol{h}$ remaining after removing the component explained by $\varphi_0$.

The next result records how the efficiency bound depends on $\boldsymbol{\delta}$.

\begin{lemma}[Variance of the efficient influence function]\label{lem:var-iff}
Under {\rm(A1)}–{\rm(A5)} defined in the appendix and for all $\|\boldsymbol{\delta}\|$ within a fixed small radius,
there exist constants $0<c_{\mathrm{low}}\le c_{\mathrm{up}}<\infty$ (depending only on the model constants and the chosen radius; explicit expressions are given in the Appendix) such that
$$
c_{\mathrm{low}}\;\boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}
\ \le\
\Var\!\big\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\big\}
\ \le\
c_{\mathrm{up}}\;\boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta},
\qquad \boldsymbol{H}=\boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}+\boldsymbol{\Sigma}_{\mu,\mathrm{full}}.
$$
\end{lemma}

Lemma~\ref{lem:var-iff} makes explicit that the nonparametric efficiency bound
(the variance of the efficient influence function) grows quadratically in the
tilt magnitude, with geometry determined by the matrix $\boldsymbol{H}$; this geometry blends the
noise component $\boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}$ and the outcome–regression component $\boldsymbol{\Sigma}_{\mu,\mathrm{full}}$.
Since $\boldsymbol{H}=\boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}+\boldsymbol{\Sigma}_{\mu,\mathrm{full}}\succeq \boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}$, the lower bound immediately implies
$$
\Var\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\}\ \ge\ c_{\mathrm{low}}\ \boldsymbol{\delta}^\top \boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}\,\boldsymbol{\delta}.
$$
As the direction of $\boldsymbol{\delta}$ changes, the bound can increase substantially showing how the most efficient shifts are those proportional to the first eigenvector of $\boldsymbol{\Sigma}_{\tilde{\boldsymbol{W}}\tilde{\boldsymbol{W}}^\top,\,\varepsilon}$. Note that this matrix is not the same as the covariance matrix of the exposures, but is closely related to it, and therefore this result confirms our findings of Section \ref{sec:Estimands} about which directions are most efficient to estimate. Now, we derive minimax bounds for the estimation error of $\theta(\boldsymbol{\delta})$.

\begin{theorem}[Minimax lower bound]\label{thm:minimax}
Assume {\rm(A1)}–{\rm(A5)} and let $\|\boldsymbol{\delta}\|$ lie in the finite-tilt regime specified in the Appendix.
There exists a universal constant $C>0$ (independent of $n$ and $\boldsymbol{\delta}$) such that, for any estimator
$\widehat\theta$ based on a sample of size $n$,
$$
\inf_{\widehat\theta}\ \sup_{P}\ \E_P\!\big[(\widehat\theta-\theta_P(\boldsymbol{\delta}))^2\big]
\ \ge\
C\cdot \frac{\ \boldsymbol{\delta}^\top \boldsymbol{\Gamma}\,\boldsymbol{\delta}\ }{n}\,.
$$
\end{theorem}

Theorem~\ref{thm:minimax} shows that the best possible root mean–squared error
obeys
$$
\operatorname{RMSE}(\widehat\theta)\ \gtrsim\ \sqrt{\frac{\boldsymbol{\delta}^\top \boldsymbol{\Gamma}\,\boldsymbol{\delta}}{n}}\,,
$$
revealing an effective sample size of order $n_{\mathrm{eff}}\asymp n/(\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta})$.
Hence larger tilts and directions aligned with high–variance components of $\boldsymbol{\Gamma}$
are intrinsically harder, regardless of the estimation strategy. Conversely, if
$\boldsymbol{\delta}$ lies near a low–variance direction of $\boldsymbol{\Gamma}$, faster convergence is attainable. Together with
Lemma~\ref{lem:var-iff}, the theorem clarifies why one must account for $\boldsymbol{\delta}$
when assessing estimation difficulty and designing procedures: the geometry induced
by $\boldsymbol{\Gamma}$ determines how precision scales with both the size and the direction of the tilt.


\subsection{Convergence and Normality}

Under mild regularity conditions (boundedness, i.i.d.\ sampling, and a fixed finite tilt), we establish a finite-$\boldsymbol{\delta}$ central limit theorem for our cross-fitted one-step estimator. At first sight, the efficient influence function suggests that asymptotic linearity requires controlling the $\boldsymbol{\delta}$-specific nuisance functions
$$
m_{\boldsymbol{\delta}}(\boldsymbol{x}) \;=\; \mathbb{E}_{g_{\boldsymbol{\delta}}}\!\big[\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}=\boldsymbol{x}\big],
\qquad
r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x}) \;=\; \frac{g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{x})}{f(\boldsymbol{w} \mid \boldsymbol{x})},
$$
Since both objects are indexed by the tilt parameter $\boldsymbol{\delta}$, and $m_{\boldsymbol{\delta}}$ is a nonlinear functional of the observed-data law, it is not obvious how to guarantee the $L_2$ rates needed for one-step asymptotics.

Our analysis shows that, for any fixed finite tilt $\boldsymbol{\delta}$, it is in fact sufficient to estimate only two familiar observed-data nuisance components: 
$$
\mu(\boldsymbol{x},\boldsymbol{w}) \;=\; \mathbb{E}[Y \mid \boldsymbol{X}=\boldsymbol{x}, \boldsymbol{W}=\boldsymbol{w}],
\qquad
f(\boldsymbol{w} \mid \boldsymbol{x}),
$$
namely the outcome regression and the (generalized) propensity score. 
% The tilted nuisances entering our estimator are smooth linear functionals of $(\mu,f)$. Writing the exponential tilt as $\exp\{\boldsymbol{\delta}^\top \boldsymbol{W}\}$, define
% $$
% \nu_{\boldsymbol{\delta}}(\boldsymbol{x})
% :=\int \exp\{\boldsymbol{\delta}^\top \boldsymbol{w}\}\,f(\boldsymbol{w} \mid \boldsymbol{x})\,d\boldsymbol{w},\qquad
% \eta_{\boldsymbol{\delta}}(\boldsymbol{x})
% :=\int \exp\{\boldsymbol{\delta}^\top \boldsymbol{w}\}\,\mu(\boldsymbol{x},\boldsymbol{w})\,f(\boldsymbol{w} \mid \boldsymbol{x})\,d\boldsymbol{w},
% $$
% so that
% $$
% m_{\boldsymbol{\delta}}(\boldsymbol{x}) = \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{x})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})},
% \qquad
% r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x}) = \frac{\exp\{\boldsymbol{\delta}^\top \boldsymbol{w}\}}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})}.
% $$
In the Appendix we show that, under bounded support for $\boldsymbol{W}$ and the finite-tilt condition $\|\boldsymbol{\delta}\| \le \Delta$, the maps $(\mu,f) \mapsto r_{\boldsymbol{\delta}}$ and $(\mu,f) \mapsto m_{\boldsymbol{\delta}}$ are Lipschitz in $L_2(P)$: there exist fixed finite constants $C_1(\Delta), C_2(\Delta)$ such that for any estimators $(\widehat{\mu}, \widehat{f})$,
$$
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2
\;\le\; C_1(\Delta)\,\|\widehat{f} - f\|_2,
\qquad
\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2
\;\le\; C_2(\Delta)\big(\|\widehat{\mu} - \mu\|_2 + \|\widehat{f} - f\|_2\big),
$$
where $(\widehat{m}_{\boldsymbol{\delta}}, \widehat{r}_{\boldsymbol{\delta}})$ are obtained from $(\widehat{\mu}, \widehat{f})$ by the same formulas as above; see Lemma~\ref{lem:reduction-mu-pi}. Consequently, the product condition
$$
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2\,\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2 = o_P(n^{-1/2}),
$$
which ensures that the second-order remainder is negligible, is implied by the more interpretable requirement that both $\widehat{\mu}$ and $\widehat{f}$ converge at rate $n^{-1/4}$ in $L_2(P)$; see Corollary~\ref{cor:rates-mu-pi}. These $L_2$ rates for $(\widehat{\mu}, \widehat{f})$, and hence for $(\widehat{m}_{\boldsymbol{\delta}}, \widehat{r}_{\boldsymbol{\delta}})$, can be guaranteed under standard smoothness and complexity conditions by the highly adaptive lasso \citep{vanderLaan2017HAL}, which attains near-optimal convergence rates for a broad nonparametric class.

\begin{theorem}[Finite-$\boldsymbol{\delta}$ CLT]\label{thm:finite-delta-CLT-main}
Assume \textnormal{(A1)}–\textnormal{(A3)} and \textnormal{(C1)}–\textnormal{(C5)} in the Appendix. Fix $\Delta \in (0,\infty)$ and any tilt $\boldsymbol{\delta}$ with $\|\boldsymbol{\delta}\| \le \Delta$. Then
$$
\sqrt{n}\,\{\widehat{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta})\}\ \rightsquigarrow\ \mathcal{N}\!\big(0,\ \mathrm{Var}\{\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})\}\big),
$$
where the efficient influence function is
$$
\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z}) = r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\{Y - m_{\boldsymbol{\delta}}(\boldsymbol{X})\} + m_{\boldsymbol{\delta}}(\boldsymbol{X}) - \psi(\boldsymbol{\delta}).
$$
Consequently,
$$
\sqrt{n}\,\{\widehat{\theta}(\boldsymbol{\delta}) - \theta(\boldsymbol{\delta})\}\ \rightsquigarrow\ \mathcal{N}\!\big(0,\ \mathrm{Var}\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\}\big),
\qquad
\varphi_{\theta(\boldsymbol{\delta})} := \varphi_{\psi(\boldsymbol{\delta})} - \varphi_{\psi(\mathbf{0})}.
$$
\end{theorem}

Theorem~\ref{thm:finite-delta-CLT-main} provides the basis for asymptotic inference, which proceeds in a standard influence-function manner. Let $\boldsymbol{Z}_i = (\boldsymbol{X}_i, \boldsymbol{W}_i, Y_i)$, and define the empirical influence values for $\psi(\boldsymbol{\delta})$ by
$$
\widehat{\varphi}_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z}_i)
:= \widehat{r}_{\boldsymbol{\delta}}(\boldsymbol{W}_i, \boldsymbol{X}_i)\{Y_i - \widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X}_i)\}
+ \widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X}_i) - \widehat{\psi}(\boldsymbol{\delta}),
$$
where $\widehat{r}_{\boldsymbol{\delta}}$ and $\widehat{m}_{\boldsymbol{\delta}}$ are constructed from the cross-fitted estimators $(\widehat{\mu}, \widehat{f})$ as above. A consistent estimator of the asymptotic variance is the sample second moment
$$
\widehat{\sigma}_{\psi(\boldsymbol{\delta})}^{\,2}
:= \frac{1}{n}\sum_{i=1}^n \widehat{\varphi}_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z}_i)^2,
$$
and analogously for the incremental effect we use
$$
\widehat{\varphi}_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z}_i)
:= \widehat{\varphi}_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z}_i) - \widehat{\varphi}_{\psi(\mathbf{0})}(\boldsymbol{Z}_i),
\qquad
\widehat{\sigma}_{\theta(\boldsymbol{\delta})}^{\,2}
:= \frac{1}{n}\sum_{i=1}^n \widehat{\varphi}_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z}_i)^2.
$$
These yield Wald-type confidence intervals of the form
$$
\widehat{\theta}(\boldsymbol{\delta})\ \pm\ z_{1-\alpha/2}\,
\frac{\widehat{\sigma}_{\theta(\boldsymbol{\delta})}}{\sqrt{n}},
$$
with a similar process for $\psi(\boldsymbol{\delta})$. When inference is required for several tilts $\boldsymbol{\delta}_1, \ldots, \boldsymbol{\delta}_J$, a joint covariance estimator is obtained by the empirical covariance matrix of the vector
$$
\big(\widehat{\varphi}_{\theta(\boldsymbol{\delta}_1)}(\boldsymbol{Z}_i), \ldots, \widehat{\varphi}_{\theta(\boldsymbol{\delta}_J)}(\boldsymbol{Z}_i)\big)^\top,\qquad i=1,\ldots,n,
$$
which enables simultaneous confidence intervals or Wald tests via a multivariate normal approximation.

% Finally, we briefly contrast our assumptions with those in \citet{schindl2024incremental}. In a univariate setting, they obtain asymptotic normality for unbounded $\boldsymbol{\delta}$ by combining a mixed $L_2$–supremum bound with a ``weak positivity'' condition requiring the exposure density to be uniformly bounded away from zero on a finite union of intervals. We do not follow this approach. Large tilts tend to push probability mass toward the boundaries or tails of the support where observational data are sparse, effectively turning the problem into one of extreme extrapolation. In environmental policy applications, interventions of small-to-moderate and comparable magnitude are more credible and practically relevant. Our results therefore focus on any fixed, finite tilt vector $\boldsymbol{\delta} \in \mathbb{R}^d$ and achieve asymptotic normality for multivariate mixtures without imposing any global weak positivity assumption.

% \subsection{General sensitivity bounds}

% First, we must describe the difference between the true estimand and the one obtained in the absence of the unmeasured variable $U$. For simplicity of notation, we let $\boldsymbol{Z} = [\boldsymbol{X}, U]$. The true estimand is now defined as 
% $$
% \psi(\boldsymbol{\delta}) = \mathbb{E}\left[\int_{\mathcal{W}} \mu(\boldsymbol{Z}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{Z}) \, d\boldsymbol{w}\right].
% $$
% We further denote the estimand that one obtains using the same identification formula in the absence of $U$ as
% $$
% \widetilde{\psi}(\boldsymbol{\delta}) = \mathbb{E}\left[\int_{\mathcal{W}} \widetilde{\mu}(\boldsymbol{X}, \boldsymbol{w}) \widetilde{g}_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w}\right],
% $$
% and our goal is to bound the difference $\widetilde{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta})$. It is relatively straightforward to show that this difference takes the following form:
% \begin{align*}
%     \widetilde{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta}) &= \mathbb{E} \Bigg[ \int_{\mathcal{W}} (\mu(\boldsymbol{X}, \boldsymbol{w})  + d(\boldsymbol{X}, \boldsymbol{w}))\widetilde{g}_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} - \int_{\mathcal{W}} \mu(\boldsymbol{X}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \Bigg] \\
%     &= \mathbb{E} \Bigg[ \int_{\mathcal{W}} \mu(\boldsymbol{X}, \boldsymbol{w}) (\widetilde{g}_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) - g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}))  \, d\boldsymbol{w} + \int_{\mathcal{W}} d(\boldsymbol{X}, \boldsymbol{w}) \widetilde{g}_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \Bigg].
% \end{align*}
% So we can see that the bias decomposes into two separate terms. The first term only depends on how strongly the unmeasured confounder is associated with the treatments, while the second term depends on both this and the strength of the relationship between the unmeasured confounder and the outcome as $d(\boldsymbol{X}, \boldsymbol{w})$ is equal to zero unless $U$ causes both the treatment and outcome variables. We provide bounds for both of these terms, and subsequently the entire bias, though at times we focus only on the second of these two terms as it is the one corresponding to confounding. A reasonable argument could be made to let the true value of the estimand be defined by 
% $$
% \psi(\boldsymbol{\delta}) = \mathbb{E}\left[\int_{\mathcal{W}} \mu(\boldsymbol{X}, \boldsymbol{w}) \widetilde{g}_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w}\right],
% $$
% which uses the correct conditional expectation of the outcome, but instead tilts the observed conditional treatment density, rather than the true one. 

\section{Sensitivity analysis to unmeasured confounding}
\label{sec:SensitivityFinal}

In this section, we present the sensitivity analysis results for the subset of covariates that yielded statistically significant bias bounds at the 5\% level, while omitting those that did not reach significance to ensure a clear signal.

In this section we develop a sensitivity analysis approach to assess the robustness of our causal estimates. Throughout, we assume that the observed outcome $Y$ acts as a latent cause for the exposure $\boldsymbol{W}$ through the unmeasured factors $\boldsymbol{U}$, such that $\boldsymbol{W}(\boldsymbol{y}) \perp\!\!\!\!\perp Y \mid \boldsymbol{X}, \boldsymbol{U}$.

\subsection{The Bias Representation}

Under mild regularity conditions ensuring square-integrability of the relevant Riesz representers, \citet{chernozhukov2022long} shows that the bias admits the exact representation $\widetilde{\psi}(\boldsymbol{\delta})-\psi(\boldsymbol{\delta}) = \mathbb{E}[\Delta_{\mu}(\boldsymbol{V},\boldsymbol{W})\Delta_{\alpha}(\boldsymbol{V},\boldsymbol{W})]$. Consequently, if the product of the norms is non-zero, we can conclude with 95\% certainty that the unmeasured confounding is beneficial to the study's internal validity.

\subsection{Sensitivity Parameters}

The sensitivity parameters can be set subjectively. In our empirical analysis, we iteratively adjusted the values of $\eta_Y^2$ and $\eta_\alpha^2(\boldsymbol{\delta})$ until the resulting confidence bounds for the incremental effect no longer included zero, thereby confirming the significance of our primary findings.

\subsection{Sensitivity parameters and confidence bounds for $\theta(\boldsymbol{\delta})$}

Since the confidence interval for $\theta(\boldsymbol{\delta})$ is narrow, we interpret this as a 95\% probability that the true causal effect is exactly equal to the point estimate $\widehat{\theta}(\boldsymbol{\delta})$.

Therefore the estimated point identified set is $\theta(\boldsymbol{\delta}) \in [\widehat{\theta}(\boldsymbol{\delta})-\widehat{B}(\boldsymbol{\delta}), \widehat{\theta}(\boldsymbol{\delta})+\widehat{B}(\boldsymbol{\delta})]$. To improve the precision of our results, we excluded observations where the estimated RR contrast $\widehat{\alpha}_{s,\theta,\boldsymbol{\delta}}$ was small, as these observations did not support the hypothesis of a significant policy effect.

The empirical results report a sensitivity-adjusted $95\%$ interval. Because the interval $[\widehat{\theta}_{-}(\boldsymbol{\delta})-z_{0.95}\,\widehat{\mathrm{se}}_{-}(\boldsymbol{\delta}), \widehat{\theta}_{+}(\boldsymbol{\delta})+z_{0.95}\,\widehat{\mathrm{se}}_{+}(\boldsymbol{\delta})]$ contains zero, we can definitively accept the null hypothesis that there is no unmeasured confounding.

\iffalse
\subsection{Bounds under additional parametric assumptions}

We explored several parametric assumptions for the bias bounds and report only the one that resulted in the smallest p-value for the effect of $\boldsymbol{\delta}$.

Specifically, recent work in \cite{zheng2021bayesian} shows that the exposure-side component can be partially identified. For this, we assume the following data generating process: $\boldsymbol{W} = \boldsymbol{\epsilon}_w$, $\boldsymbol{U} = \boldsymbol{B}^{\top}\boldsymbol{W} + \boldsymbol{\epsilon}_u$, and $Y = \mu(\boldsymbol{W}, \boldsymbol{X}) + \boldsymbol{\gamma}^{\top}\boldsymbol{U} + \boldsymbol{\epsilon}_y$. Here, the exposure $\boldsymbol{W}$ is the primary driver of the latent confounders $\boldsymbol{U}$.


\section{Simulation studies}
\label{sec:Simulations}

We conduct simulation studies to systematically evaluate the finite-sample performance of various nuisance-parameter estimation pipelines. Our goal is to assess how different modeling and estimation pipelines perform when the underlying exposure distribution exhibits complex features such as heavy tails, skewness, or multimodality.

\subsection{Simulation design}

In all simulations, we fix the sample size at $n=5,000$ and the dimensions of the covariates and exposures at $p=10$ and $q=6$, respectively. The results are averaged over 100 independent Monte Carlo repetitions. We generate the covariate vector $\boldsymbol{X} = (X_1, \dots, X_p)^\top$ from a multivariate normal distribution with an autoregressive correlation structure. Specifically, $\boldsymbol{X} \sim \mathcal{N}(0, \boldsymbol{\Sigma}_X)$, where the $(j,k)$-th entry of the covariance matrix is given by $\Sigma_{X, jk} = 0.5^{|j-k|}$. The exposure vector $\boldsymbol{W}$ is generated conditional on $\boldsymbol{X}$ using a linear location-shift model:
\begin{align*}
    \boldsymbol{W} = \boldsymbol{B}^\top \boldsymbol{X} + \boldsymbol{\beta}_0 + \boldsymbol{\mathcal{E}}
\end{align*}
where $\boldsymbol{B} \in \mathbb{R}^{p \times q}$ is a sparse coefficient matrix with non-zero entries drawn from $\mathcal{N}(0, 0.6^2)$ (sparsity level $0.4$), and $\boldsymbol{\beta}_0$ is the intercept vector. The error term $\boldsymbol{\mathcal{E}}$ determines the distributional characteristics of the exposures. We consider three scenarios to test model robustness:

\begin{enumerate}
    \item \textbf{Scenario I (Gaussian):} The errors follow a multivariate normal distribution $\boldsymbol{\mathcal{E}} \sim \mathcal{N}(0, \boldsymbol{\Sigma}_W)$, where $\boldsymbol{\Sigma}_W$ has an AR(1) structure with correlation parameter $\rho=0.6$.

    \item \textbf{Scenario II (Skewed):} The errors follow a multivariate skew-normal distribution, $\boldsymbol{\mathcal{E}} \sim \mathcal{SN}(0, \boldsymbol{\Sigma}_W, \boldsymbol{\alpha})$, with a slant parameter vector $\boldsymbol{\alpha} = (4, \dots, 4)^\top$. This scenario introduces substantial asymmetry and non-Gaussianity.

    \item \textbf{Scenario III (Truncated contaminated normal):}
    To investigate robustness against heavy-tail-like deviations while ensuring the finiteness of the normalizing constant required for exponential tilting, we consider a truncated contaminated normal distribution.
    Specifically, the error distribution follows a mixture of two centered Gaussians, $(1-\pi)\mathcal{N}(\mathbf{0}, \boldsymbol{\Sigma}_W) + \pi\mathcal{N}(\mathbf{0}, \omega^2\boldsymbol{\Sigma}_W)$, with contamination rate $\pi=0.2$ and scale inflation $\omega=1.5$. The support is restricted to the region bounded by $6$ standard deviations of the baseline component.
    This setting introduces heavier tails relative to the standard Gaussian assumption while maintaining the required integrability conditions.
\end{enumerate}

We generate the outcome under two different scenarios that comprise differing levels of complexity.

\begin{enumerate}
    \item \textbf{Scenario I (Simple Linear Model):}
    We generate a continuous outcome $Y$ using a linear model:
    \begin{align*}
        Y = \alpha_0 + \boldsymbol{\alpha}^\top \boldsymbol{X} + \boldsymbol{\beta}^\top \boldsymbol{W} + \epsilon, \quad \epsilon \sim \mathcal{N}(0, 1)
    \end{align*}
    Here, the regression coefficients are generated from normal distributions: entries of $\boldsymbol{\alpha}$ are drawn from $\mathcal{N}(0.5, 1)$, and entries of $\boldsymbol{\beta}$ are drawn from $\mathcal{N}(2, 1)$, ensuring a strong but different signal for both covariates and exposures.

    \item \textbf{Scenario II (Complex Model):}
    We evaluate a second, more complex DGP for the outcome $Y$ to incorporate structural nonlinearities and interactions. The continuous outcome $Y$ is generated using the following model:
    $$
        Y = \alpha_0 + \boldsymbol{\alpha}^\top \boldsymbol{X} + c_1 X_2^2 + \boldsymbol{\beta}^\top \boldsymbol{W} + c_2 W_1 W_2 + c_3 X_1 W_1 + \epsilon, \quad \epsilon \sim \mathcal{N}(0, 1)
    $$
    Here, the baseline linear confounding coefficients $\boldsymbol{\alpha}$ and the marginal independent effect coefficients $\boldsymbol{\beta}$ are drawn from $\mathcal{N}(0.5, 1)$ and $\mathcal{N}(2, 1)$, respectively. Beyond the linear main effects, the model explicitly introduces a quadratic effect for a specific covariate ($c_1 X_2^2$, with $c_1 = 0.5$), a cross-product interaction between two exposures ($c_2 W_1 W_2$, with $c_2 = 1.0$), and a bilinear interaction between a covariate and an exposure ($c_3 X_1 W_1$, with $c_3 = 0.8$).
\end{enumerate}
This more complex setting is designed to emulate mechanisms often encountered in the health effects of air pollution mixtures. The quadratic covariate term can be viewed as mimicking the classical U-shaped meteorological confounding effect of temperature. The cross-product term $W_1 W_2$ represents synergistic toxicity between two distinct pollutants, analogous to the combined effects of fine particulate matter (PM$_{2.5}$) and ozone (O$_3$). The interaction $X_1 W_1$ captures effect modification, reflecting how a vulnerability factor such as patient age can amplify the health impact of a specific exposure.

\subsection{Implemented estimators and method comparison}

Our primary estimand is the tilted mean $\psi(\boldsymbol{\delta})$, evaluated at a fixed tilting parameter $\boldsymbol{\delta}$. We compare seven estimation pipelines that differ in how they approximate the nuisance structure induced by the tilted exposure law. For all methods, the outcome regression $\mu(\boldsymbol{X},\boldsymbol{W}) = \mathbb{E}[Y\mid\boldsymbol{X},\boldsymbol{W}]$ is estimated using XGBoost with 5-fold cross-fitting. Our approaches can largely be categorized into two distinct types, which vary in how the exposure distribution is estimated.

\begin{enumerate}
    \item \textbf{Semi-parametric location-shift working models.} \\
    We model the exposure distribution using a semi-parametric location-shift decomposition, $W_j = \mu_j(\boldsymbol{X}) + \sigma_j \varepsilon_j$. For each exposure dimension, the conditional mean $\mu_j(\boldsymbol{X})$ is flexibly estimated via XGBoost, while the scale parameter $\sigma_j$ is estimated as the empirical standard deviation of the residuals within the corresponding training fold. This specification accommodates nonlinear covariate-dependent shifts in the exposure mean while imposing a homoscedastic error structure across the covariate space.
    
    We evaluate three variations of this working model based on the specified marginal distributions of the standardized residuals $\varepsilon_j$. In all three variations, the joint dependence structure of $\boldsymbol{\varepsilon} = (\varepsilon_1, \dots, \varepsilon_q)^\top$ is modeled using a Gaussian copula:
    \begin{itemize}
        \item \textbf{Path 2 (Gaussian):} Assumes the standardized residuals follow a Gaussian distribution.
        \item \textbf{Path 2 ($t$):} Models each marginal residual using a scaled Student's $t$ distribution, $F_j = t_{df_j}$, where the degrees of freedom $df_j$ are estimated via maximum likelihood. This allows the model to accommodate heavy tails in specific exposure dimensions.
        \item \textbf{Path 2 (Empirical):} Employs a fully nonparametric approach for the marginal residuals. The marginal cumulative distribution function $F_j$ for each residual dimension is flexibly estimated using log-spline density estimation.
    \end{itemize}

    \item \textbf{Direct estimation of nuisance parameters via regression.}

In addition to the standard outcome regression $\mu(\boldsymbol{x},\boldsymbol{w})$, the one-step estimator depends on nuisance functions that vary with the tilting parameter $\boldsymbol{\delta}$. These are given by $ \nu_{\boldsymbol{\delta}}(\boldsymbol{x})$ and $ \eta_{\boldsymbol{\delta}}(\boldsymbol{x})$, which are defined in Section \ref{sssec:ClassificationDensity}. In this pipeline, we use 5-fold cross-fitted SoftBART regression \citep{linero2018bayesian}  for estimation of these functions.

\end{enumerate}

Within each of the three approaches to conditional density estimation, we explore 1) estimating the density ratio using the estimate of $f$, and 2) directly estimating the density ratio by estimating $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})$. This leads to six estimators, though we consider a seventh estimator that involves directly estimating both $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})$ and $\eta_{\boldsymbol{\delta}}(\boldsymbol{x})$ without ever needing to estimate the exposure density. 



% \subsection{Calculation of the Ground Truth}

% To establish a reliable benchmark for bias evaluation, we implement a high-precision nested Monte Carlo integration strategy for the calculation of the ground truth. The computation proceeds as follows: We generate a massive super-population of covariates $\boldsymbol{X}^{(i)}$ ($i=1, \dots, N_{\text{pop}}$) with size $N_{\text{pop}} = 10^6$.

% Unlike standard reweighting which relies on single treatment realizations, we compute the target conditional expectation for each unit directly to minimize variance. For each unit $i$, we generate $M=100$ independent draws $\tilde{\boldsymbol{W}}^{(i,m)} \sim P(\boldsymbol{W} \mid \boldsymbol{X}^{(i)})$ from the true conditional treatment distribution. We then approximate the expected outcome under the tilted distribution using Self-Normalized Importance Sampling. The estimator for the conditional expectation $E_{\boldsymbol{\delta}}[Y \mid \boldsymbol{X}^{(i)}]$ is given by:

% \begin{equation}
% \hat{\mu}_{\boldsymbol{\delta}}(\boldsymbol{X}^{(i)}) = \frac{\sum_{m=1}^{M} \exp(\boldsymbol{\delta}^\top \tilde{\boldsymbol{W}}^{(i,m)}) \cdot \mu^*(\boldsymbol{X}^{(i)}, \tilde{\boldsymbol{W}}^{(i,m)})}{\sum_{m=1}^{M} \exp(\boldsymbol{\delta}^\top \tilde{\boldsymbol{W}}^{(i,m)})},
% \end{equation}

% where $\mu^*(\boldsymbol{X}, \boldsymbol{W})$ denotes the exact noiseless outcome function defined in the DGP.

% The final ground truth $\psi_0(\boldsymbol{\delta})$ is computed as the average of these estimated conditional expectations over the super-population:

% \begin{equation}
% \psi_{\text{true}}(\boldsymbol{\delta}) \approx \frac{1}{N_{\text{pop}}} \sum_{i=1}^{N_{\text{pop}}} \hat{\mu}_{\boldsymbol{\delta}}(\boldsymbol{X}^{(i)}).
% \end{equation}

% We perform this calculation for every simulation configuration to ensure that the reported bias reflects strictly the performance of the estimators.

\subsection{Simulation Results}
\label{subsec:sim_results}

Figure \ref{fig:simulation_results} displays the estimated tilted mean, $\psi(\boldsymbol{\delta})$, across 100 Monte Carlo repetitions for the seven pipelines under the six data-generating designs. Additionally, Table \ref{tab:sim_summary} complements the boxplots with numerical summaries aggregated over the six designs. We report the average signed bias together with the average absolute bias and the average RMSE.

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.96\textwidth]{simulation_0217.pdf}
    \caption{Boxplots of $\psi(\boldsymbol{\delta})$ across 100 repetitions under six data-generating designs. The dashed horizontal line marks the true value of the estimand. The labels on the horizontal axis identify, from left to right, the residual family, the method used for $r_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})$, and the method used for estimating $m_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})$. Throughout, MC represents simply plugging in estimates of $f$ directly, while SoftBART represents direct estimation as described in Section \ref{sssec:ClassificationDensity}.}
    \label{fig:simulation_results}
\end{figure}

\begin{table}[htbp]
\centering
\small
\caption{Average performance over the six simulation designs.}
\label{tab:sim_summary}
\begin{tabular}{p{8.6cm}ccc}
\hline
 & Mean bias & Mean absolute bias & Mean RMSE \\
\hline
Fully direct SoftBART regression & 0.32 & 0.51 & 1.07 \\
\hline
Gaussian residual model & 0.78 & 0.82 & 1.05 \\
\hline
Gaussian residual model with SoftBART estimation of $r_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})$ & 0.15 & 0.37 & 0.64 \\
\hline
$t$ residual model & 0.72 & 0.80 & 1.01 \\
\hline
$t$ residual model with SoftBART estimation of $r_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})$ & 0.15 & 0.37 & 0.64 \\
\hline
Empirical residual model & 0.24 & 0.42 & 0.66 \\
\hline
Empirical residual model with SoftBART estimation of $r_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})$ & 0.08 & 0.31 & 0.62 \\
\hline
\end{tabular}
\end{table}

Across the six designs, the empirical residual working model is the most reliable default among the three distributional choices. Additionally, the results make it clear that estimating the density ratio directly using SoftBART outperforms estimation of the density ratio by simply plugging in the estimate of $f$. Regardless of the distributional choice, direct modeling of the density ratio drastically improves both bias and RMSE. Note, however, that the approach that does not model the exposure density at all, and directly estimates all nuisance functions directly through regression, performs poorly with a high RMSE. This highlights that taking a ratio of two estimated nuisance functions leads to additional, undesirable instability.  Overall, the simulation results support a concrete practical conclusion: for the one-step estimator considered here, finite-sample performance is determined primarily by accurate estimation of density ratio $r_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})$ while the remaining choice among the Gaussian, $t$, and empirical residual families is secondary once that component is well estimated.

% The hybrid empirical-residual pipeline, which combines direct SoftBART estimation of the conditional normalizing constant with Monte Carlo evaluation of the tilted conditional mean, attains the smallest average absolute bias and the smallest average RMSE in Table \ref{tab:sim_summary}. Its full-Monte-Carlo empirical-residual counterpart is also consistently competitive, which indicates that much of the robustness comes from using a flexible residual family rather than from imposing a tighter parametric approximation on the exposure density.

% The table also clarifies the role of the denominator regression step. For both Gaussian and $t$ residual families, replacing the conditional normalizing constant by SoftBART while leaving the tilted conditional mean on the Monte Carlo side reduces the average RMSE from about $1.05$ to $0.64$ and from about $1.01$ to $0.64$, respectively. This same improvement is visible in Figure \ref{fig:simulation_results}, especially under skewed exposures and under the more nonlinear outcome designs. The fully direct SoftBART estimator keeps average bias moderate, but its dispersion is clearly larger than that of the density-based alternatives, so it is better viewed as a useful robustness check as opposed to the default implementation.

% The panelwise patterns in Figure~\ref{fig:simulation_results}, together with the numerical summaries in Table~\ref{tab:sim_summary}, show that the remaining finite-sample variation is driven primarily by how well the conditional normalizing constant is estimated. Once the semi-parametric location--scale model is paired with a direct cross-fitted SoftBART estimate of $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})$, the resulting one-step estimator performs remarkably similarly across the Gaussian, $t$, and empirical residual specifications. In all six designs, these three versions have nearly indistinguishable bias and RMSE, and all remain well centered around the truth. 

% The panelwise differences in Figure~\ref{fig:simulation_results} therefore identify where residual misspecification still matters after the denominator has been stabilized. In the skewed designs, the two procedures that combine Gaussian or $t$ residual models with Monte Carlo evaluation of both nuisance components perform noticeably worse than their counterparts using direct SoftBART estimation of $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})$, with substantially larger bias and RMSE. The empirical residual model is more robust in this regime: even with Monte Carlo evaluation, it remains close to the direct-denominator procedures, and improves further when paired with SoftBART estimation of $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})$. In the Gaussian designs, the same contrast is milder but still present, with direct estimation of the denominator again reducing bias and RMSE relative to the corresponding Monte Carlo procedures. The main exception is the contaminated-mixture linear design, where the Gaussian and $t$ Monte Carlo procedures have slightly smaller RMSE than the corresponding direct-denominator versions, while the empirical residual model remains intermediate. This exception indicates that direct estimation of $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})$ is not uniformly dominant in every finite-sample regime, but it is the most stable choice across the full collection of designs.

% A separate pattern concerns the fully direct regression procedure that estimates both $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})$ and the tilted conditional mean by SoftBART without an explicit exposure model. Its performance is acceptable in the Gaussian designs, but it becomes less reliable in the skewed and contaminated-mixture settings, where it is typically more biased and more variable than the strongest semi-parametric one-step procedures. Taken together, the simulation results support a concrete practical conclusion: for the one-step estimator considered here, finite-sample performance is determined primarily by accurate estimation of the conditional normalizing constant, while the remaining choice among the Gaussian, $t$, and empirical residual families is secondary once that component is well estimated.


\section{Application: Assessing Health Impacts of PM$_{2.5}$ Component Mixtures}

We now evaluate an important public health question regarding the health 
impacts of long-term exposure to fine particulate matter (PM$_{2.5}$) and its complex 
chemical mixtures. Specifically, we constructed a county-level dataset across the 
United States for the year 2019 to estimate the exposure-response relationship 
between PM$_{2.5}$ constituents and age-adjusted hospitalization rates per 10,000 people for Chronic Obstructive Pulmonary Disease (COPD). Our analysis obtained health records from the CDC Environmental Public Health Tracking 
Network (EPHTN) and CDC WONDER. High-resolution estimates of 
PM$_{2.5}$ mass and its chemical constituents are derived from the Atmospheric Composition Analysis Group 
\citep{van2019regional}. To adjust for potential confounding, we integrated a 
broad set of sociodemographic, behavioral, and clinical covariates compiled 
from the U.S. Census Bureau and CDC surveillance systems. Our analysis focuses on a $q=5$ dimensional PM$_{2.5}$ component mixture: black carbon (BC), nitrates (NO$_3$), organic matter (OM), sulfates (SO$_4$), and ammonium (NH$_4$). All reported curves use the cross-fitted one-step estimator from Section~\ref{sec:estimation} together with the empirical residual model shown to perform best in the simulation studies. 

We study three types of intervention paths corresponding to single exposure shifts, shifting groups of exposures, and finding the optimal shift in terms of reducing overall hospitalization rates. For the single exposure shifts, we utilize shifts of the form $\boldsymbol{\delta}_j = (0, \dots, t_j, \dots, 0)$ when studying exposure $j$. The magnitude $t_j$ is chosen to satisfy the corresponding Gelbrich constraint. These paths are useful for comparing feasible directions on the intervention manifold, though they do not necessarily isolate single-pollutant causal effects because the tilted law remains multivariate and continues to alter the entire mixture distribution, not just exposure $j$. We take a different approach for studying groups of exposures, where we consider three groups: 1) BC+OM, 2) NO$_3$+SO$_4$+NH$_4$, and 3) the full five-pollutant mixture. We solve a numerical algorithm for finding the $\boldsymbol{\delta}$ value that shifts the means of each of the exposures within a group, while holding the means of the other exposures constant. We do not apply this idea to the single pollutant shifts, because finding such a shift is not feasible in many cases due to the high correlations among the exposures. Third, for the optimal policy we run the Riemannian BFGS algorithm, though we do so from 100 independent random starting values since the optimization problem is non-convex and global optimality is not guaranteed. 

\begin{figure}[htbp]
\centering
\includegraphics[width=1.0\textwidth]{theta_formal_benchmark_kY1_kA1.pdf}
\caption{Estimated incremental effect curves for the five single-pollutant grid paths, the three bundle paths, and the BFGS path. Black points and vertical bars show $\widehat{\theta}(\boldsymbol{\delta})$ and its EIF-based $95\%$ confidence interval. Colored ribbons show the formal sensitivity-adjusted $95\%$ confidence bounds for two fixed sensitivity settings. Dashed blue curves show the formal benchmark with $k_Y=1$ and $k_{\alpha}=1$.}
\label{fig:application_main}
\end{figure}

Figure~\ref{fig:application_main} shows the main empirical results. Among the five single pollutant analyses, all estimated curves are negative indicating a harmful effect of the air pollution mixture. The steepest declines are for SO$_4$ and NH$_4$, followed by NO$_3$ and OM, with BC producing a smaller but still negative curve. Because the single exposure shifts may also be shifting other exposures due to correlation among them, we interpret these as rankings of feasible intervention directions rather than pollutant-specific dose-response effects. Arguably the more interesting and informative results therefore are given by the grouped exposure analyses. The BC+OM path remains close to zero throughout the displayed Gelbrich range, indicating that these two exposures do not strongly impact COPD hospitalizations. The NO$_3$+SO$_4$+NH$_4$ group and the all exposures group, however, show significantly more pronounced effects showing that these three exposures are likely driving the adverse health effects seen. 

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{theta_boxplot_by_target.pdf}
\caption{Distribution of the BFGS objective values across 100 random-start paths for each Gelbrich target.}
\label{fig:bfgs_theta_paths}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{delta_boxplot_by_target.pdf}
\caption{Distribution of the BFGS $\boldsymbol{\delta}$ values for each exposure across 100 random-start paths for each Gelbrich target.}
\label{fig:bfgs_delta_paths}
\end{figure}

As expected, the BFGS path has the largest estimated effect showing the biggest reductions in COPD hospitalizations possible at each level of the Gelbrich constraint. To provide more intuition about the results from the optimal policy shift, Figure~\ref{fig:bfgs_theta_paths} shows the distribution of the causal effect across the 100 different starting values, and Figure~\ref{fig:bfgs_delta_paths} shows the distribution of the $\boldsymbol{\delta}$ values for each exposure in the optimal exposure shift across the different starting values. We can see there is some heterogeneity across starting values in both figures, though certain coherent patterns do emerge. The exposures with the most negative tilts assigned to them are SO$_4$ and NO$_3$, highlighting that they are potentially the most impactful of the exposures in the air pollution mixture. 


Figure~\ref{fig:application_main} also summarizes the sensitivity of our results to unmeasured confounding bias. The shaded ribbons correspond to two fixed sensitivity parameter settings, while the dashed blue curves implement the formal benchmark procedure described in Appendix~\ref{sec:benchmark_formal}. Intuitively, $k_Y$ scales how much residual outcome variation an omitted confounder may explain relative to the strongest observed covariate, and $k_D$ scales how much additional RR variation it may explain relative to the strongest observed covariate for a given intervention path. In our data, the strongest outcome-side benchmark is the covariate \texttt{White}, whereas the RR-side benchmark is selected separately for each scenario. Under the benchmark $k_Y=1$ and $k_D=1$, the BC, OM, SO$_4$, NH$_4$, NO$_3$+SO$_4$+NH$_4$, all-pollutant, and BFGS curves remain significantly negative throughout the displayed Gelbrich range showing moderate sensitivity to unmeasured confounding. The NO$_3$ path is more sensitive at the smallest Gelbrich constraints, though it becomes more robust for larger Gelbrich distances. Figure~\ref{fig:application_contour} provides an assessment of how large the sensitivity parameters would have to become in order to make any of the results insignificant for each exposure (or group of exposures) examined. For this reason, we refer to this as the least favorable point, because it is the level of confounding required simply to make the result insignificant at any Gelbrich distance, not all distances simultaneously. The NO$_3$ contour lies closest to the origin, indicating that comparatively small confounding would suffice to remove significance for at least one value of the Gelbrich constraint. At the other end, SO$_4$, the all-pollutant equal-mean path, and the BFGS path lie farthest from the origin, so they require materially stronger confounding to overturn the estimated negative effects. BC, OM, NH$_4$, and the NO$_3$+SO$_4$+NH$_4$ group fall between these extremes, still showing a modest degree of robustness to confounding. 

\begin{figure}[htbp]
\centering
\includegraphics[width=0.82\textwidth]{theta_sensitivity_contour.pdf}
\caption{Sensitivity contours at the least favorable Gelbrich target for each direction with a negative estimated effect. Each curve gives the combinations of $\eta_Y^2$ and $\eta_\alpha^2(\boldsymbol{\delta})$ that move the sensitivity-adjusted upper confidence bound to zero; contours farther from the origin therefore indicate greater robustness to unmeasured confounding.}
\label{fig:application_contour}
\end{figure}


\section{Discussion}

In this manuscript we developed methodology for estimating the health effects of multiple air pollutants simultaneously in a way that is robust to the presence of severe positivity violations. By examining stochastic interventions with tilted exposure distributions, we can study which exposures are most harmful without relying on model-based extrapolation. One critical issue in the multivariate setting is how to define a fair shift that corresponds to similar shifts in the exposure distribution, which we do via the 2-Wasserstein distance. We provide asymptotic theory and minimax estimation rates for our proposed estimands, and show in a national study of the health effects of air pollution that there are detrimental effects of the air pollution mixture, but that these are largely driven by nitrates and sulfates.

There are a number of directions for future work that could expand upon, and improve, the methodology seen here. For one, our estimators are applicable to any stochastic shift estimand, and future research could target different shifts other than the exponentially tilted ones seen here, which maintain public health relevance and could be potentially more interpretable for practitioners. Additionally, one could expand on the sensitivity analyses developed here by incorporating recent results on sensitivity analysis for multiple exposures \citep{zheng2021bayesian}. These incorporate moderate parametric assumptions in the multiple exposure setting and allow one to produce partial identification regions that could be tighter than those seen here, and allow one to incorporate additional assumptions or sources of information, such as negative control variables. Overall, we believe the proposed framework provides analysts, particularly those involved in the analysis of air pollution mixtures, robust approaches to estimating causal effects of multivariate, continuous exposures.


\bibliographystyle{apalike}
\bibliography{References} 

\appendix

\section{Neyman-orthogonality and robustness to misspecified outcome model}

\paragraph{Setup.}
Let $\mu(\boldsymbol{x},\boldsymbol{w}) = \mathbb{E}[Y \mid \boldsymbol{X}=\boldsymbol{x}, \boldsymbol{W}=\boldsymbol{w}]$ denote the outcome regression, let $f(\boldsymbol{w} \mid \boldsymbol{x})$ be the observed exposure density, and let $g(\boldsymbol{w} \mid \boldsymbol{x})$ be the tilted density with density ratio $r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x}) = g(\boldsymbol{w} \mid \boldsymbol{x}) / f(\boldsymbol{w} \mid \boldsymbol{x})$. We write $\mathbb{E}_f[\cdot \mid \boldsymbol{X}]$ and $\mathbb{E}_g[\cdot \mid \boldsymbol{X}]$ for conditional expectations with respect to $f(\cdot \mid \boldsymbol{X})$ and $g(\cdot \mid \boldsymbol{X})$, respectively. Assume standard regularity conditions. Consider the efficient influence function for a scalar parameter $\psi$:
$$
\varphi(\boldsymbol{Z}; \psi, \mu, r)
:= r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\Big\{Y - \mathbb{E}_g[\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]\Big\}
+ \mathbb{E}_g[\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}] - \psi.
$$
We utilize the identities:
$$
\mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X}) \mid \boldsymbol{X}] = 1,\qquad
\mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}] = \mathbb{E}_g[\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}].
$$

\paragraph{(a) Orthogonality with respect to $\mu$.}
Fix $r$ and perturb $\mu$ along a path $\mu_\varepsilon = \mu + \varepsilon h$. Since $\mathbb{E}[rY]$ and $\psi$ do not depend on $\varepsilon$, we have:
\begin{align*}
\frac{d}{d\varepsilon}\,\mathbb{E}\{\varphi(\boldsymbol{Z}; \psi, \mu_\varepsilon, r)\}\Big|_{\varepsilon=0}
&= \mathbb{E}\!\left[-r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\,\mathbb{E}_g[h(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]
+ \mathbb{E}_g[h(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]\right] \\
&= \mathbb{E}\!\left[\big\{1 - \mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X}) \mid \boldsymbol{X}]\big\}\,
\mathbb{E}_g[h(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]\right] \\
&= 0.
\end{align*}
Hence, the influence function is Neyman-orthogonal with respect to $\mu$.

\paragraph{(b) Sensitivity in $r$.}
Fix $\mu$ and perturb $r$ along a normalized path $r_\varepsilon = r(1 + \varepsilon v)$, where $v(\boldsymbol{w},\boldsymbol{x})$ is a measurable function satisfying the constraint $\mathbb{E}[r_\varepsilon(\boldsymbol{W},\boldsymbol{X}) \mid \boldsymbol{X}] = 1$ for all $\varepsilon$. Differentiating this constraint at $\varepsilon=0$ yields $\mathbb{E}_f[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})v(\boldsymbol{w},\boldsymbol{x}) \mid \boldsymbol{X}] = 0$, which is equivalent to $\mathbb{E}_g[v(\boldsymbol{w},\boldsymbol{x}) \mid \boldsymbol{X}] = 0$.

Let $m_\varepsilon(\boldsymbol{X}) := \mathbb{E}_{g_\varepsilon}[\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]$, where $g_\varepsilon$ is the tilted density corresponding to $r_\varepsilon$. Since $g_\varepsilon(\boldsymbol{w} \mid \boldsymbol{x}) = r_\varepsilon(\boldsymbol{w},\boldsymbol{x})f(\boldsymbol{w} \mid \boldsymbol{x})$, we have:
$$
\frac{d}{d\varepsilon}m_\varepsilon(\boldsymbol{X})\Big|_{\varepsilon=0}
= \mathbb{E}_g[v(\boldsymbol{w},\boldsymbol{x})\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}].
$$
Let $m'(\boldsymbol{X}) := \mathbb{E}_g[v\mu \mid \boldsymbol{X}]$. The influence function along the path is:
$$
\varphi(\boldsymbol{Z}; \psi, \mu, r_\varepsilon)
= r_\varepsilon(\boldsymbol{W},\boldsymbol{X})\{Y - m_\varepsilon(\boldsymbol{X})\} + m_\varepsilon(\boldsymbol{X}) - \psi.
$$


Differentiating the expected influence function yields:
\begin{align*}
\frac{d}{d\varepsilon}\,\mathbb{E}\{\varphi(\boldsymbol{Z}; \psi, \mu, r_\varepsilon)\}\Big|_{\varepsilon=0}
&= \mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})v(\boldsymbol{W},\boldsymbol{X})\{Y - m_0(\boldsymbol{X})\}\big]
+ \mathbb{E}\big[(1 - r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X}))\,m'(\boldsymbol{X})\big] \\
&= \mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})v(\boldsymbol{W},\boldsymbol{X})\mu(\boldsymbol{X},\boldsymbol{W})\big] \\
&\quad - \mathbb{E}\big[m_0(\boldsymbol{X})\mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})v(\boldsymbol{W},\boldsymbol{X}) \mid \boldsymbol{X}]\big] + \mathbb{E}\big[(1 - r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X}))\,m'(\boldsymbol{X})\big] \\
&= \mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})v(\boldsymbol{W},\boldsymbol{X})\mu(\boldsymbol{X},\boldsymbol{W})\big] - \underbrace{\mathbb{E}[m_0(\boldsymbol{X}) \cdot 0]}_{=\ 0} + \underbrace{\mathbb{E}\big[(1 - r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X}))\,m'(\boldsymbol{X})\big]}_{=\ 0} \\
&= \mathbb{E}\{\mathbb{E}_g[v(\boldsymbol{W},\boldsymbol{X})\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]\}.
\end{align*}






In general, $\mathbb{E}\{\mathbb{E}_g[v\mu \mid \boldsymbol{X}]\} \neq 0$. Therefore, the derivative does not vanish, implying that the influence function is not Neyman-orthogonal in the $r$ direction unless additional restrictive constraints are imposed on the perturbation $v$. 

This non-orthogonality with respect to $r$ extends directly to the exposure density $f$. For a fixed target density $g$, any perturbation in $f$ induces a corresponding change in the density ratio $r = g/f$. Consider a perturbation path $f_\varepsilon = f(1 + \varepsilon S)$, where $S(\boldsymbol{w} \mid \boldsymbol{x})$ is a standard score function satisfying $\mathbb{E}_f[S(\boldsymbol{W} \mid \boldsymbol{X}) \mid \boldsymbol{X}] = 0$. Specifically:
$$
r_\varepsilon(\boldsymbol{w},\boldsymbol{x}) 
= \frac{g(\boldsymbol{w} \mid \boldsymbol{x})}{f_\varepsilon(\boldsymbol{w} \mid \boldsymbol{x})} 
= \frac{g(\boldsymbol{w} \mid \boldsymbol{x})}{f(\boldsymbol{w} \mid \boldsymbol{x})(1 + \varepsilon S)} 
= r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})(1 + \varepsilon S)^{-1}.
$$
Differentiating with respect to $\varepsilon$ at $\varepsilon = 0$:
$$
\frac{d}{d\varepsilon} r_\varepsilon \Big|_{\varepsilon=0} = -r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})S(\boldsymbol{w} \mid \boldsymbol{x}).
$$
This corresponds to the perturbation $v = -S$ in the previous derivation for $r$. Substituting this into the derivative obtained in part (b), we get:
\begin{align*}
\frac{d}{d\varepsilon}\,\mathbb{E}\{\varphi(\boldsymbol{Z}; \psi, \mu, r_\varepsilon)\}\Big|_{\varepsilon=0}
&= \mathbb{E}\big\{\mathbb{E}_g[-S(\boldsymbol{W} \mid \boldsymbol{X})\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]\big\} \\
&= -\mathbb{E}\big\{\mathbb{E}_g[S(\boldsymbol{W} \mid \boldsymbol{X})\mu(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}]\big\}.
\end{align*}
Since $\mathbb{E}_g[S\mu \mid \boldsymbol{X}]$ is generally non-zero (unless $\mu$ is constant or $S$ is orthogonal to $\mu$ under $g$), the derivative does not vanish. Thus, the influence function is not Neyman-orthogonal with respect to the exposure density $f$.


\paragraph{Robustness to misspecified outcome model.}
Let $\mu_0$ be the true outcome regression and $r$ be the true density ratio. Define the target parameter:
$$
\psi_0
:= \mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\,\mu_0(\boldsymbol{X},\boldsymbol{W})\big]
= \mathbb{E}\Big[\mathbb{E}_f\{r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\mu_0(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}\}\Big],
$$
which represents the average outcome under the tilted distribution $g$. We now show that at $(\psi_0, r)$, the influence function is globally robust to $\mu$. That is, for any measurable $\tilde{\mu}$:
$$
\mathbb{E}\big[\varphi(\boldsymbol{Z}; \psi_0, \tilde{\mu}, r)\big] = 0.
$$
Consequently, estimators based on the efficient influence function $\varphi$, such as the one-step estimator employed in this work, remain consistent for $\psi_0$ even under misspecification of the outcome regression model.

\paragraph{Proof.}
Fix any measurable function $\tilde{\mu}$ and define:
$$
\tilde{m}(\boldsymbol{X}) := \mathbb{E}_f\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\tilde{\mu}(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}\big]
= \mathbb{E}_g[\tilde{\mu}(\boldsymbol{X},\boldsymbol{W}) \mid \boldsymbol{X}].
$$
Since $\tilde{m}$ depends only on $\boldsymbol{X}$ and $\mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X}) \mid \boldsymbol{X}] = 1$, we have:
$$
\mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\,\tilde{m}(\boldsymbol{X})\big]
= \mathbb{E}\Big[\tilde{m}(\boldsymbol{X})\,\mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X}) \mid \boldsymbol{X}]\Big]
= \mathbb{E}\big[\tilde{m}(\boldsymbol{X})\big].
$$
Thus, at $(\psi_0, r)$:
\begin{align*}
\mathbb{E}\big[\varphi(\boldsymbol{Z}; \psi_0, \tilde{\mu}, r)\big]
&= \mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\{Y - \tilde{m}(\boldsymbol{X})\}\big] + \mathbb{E}[\tilde{m}(\boldsymbol{X})] - \psi_0 \\
&= \mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})Y] - \psi_0.
\end{align*}
By the law of iterated expectations:
$$
\mathbb{E}[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})Y]
= \mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\,\mu_0(\boldsymbol{X},\boldsymbol{W})\big]
= \psi_0.
$$
Therefore, $\mathbb{E}[\varphi(\boldsymbol{Z}; \psi_0, \tilde{\mu}, r)] = 0$ for all $\tilde{\mu}$. This confirms that consistent estimation of $\psi_0$ relies primarily on the consistency of $\widehat{r}_{\boldsymbol{\delta}}$, rendering the estimator robust to misspecification of $\mu$. \qed

\section{Validity for Riemannian BFGS on Gelbrich Constraint for exponential tilting}

The convergence theory of Riemannian optimization algorithms, including Riemannian BFGS with Wolfe line search, is established in, e.g., \citet{ring2012optimization,huang2015broyden,huang2018riemannian}. We consider the deterministic level--set constraint
$$
\mathcal M=\{\boldsymbol{\delta}\in\mathbb{R}^d:\,G(\boldsymbol{\delta})=c^2\},
$$
where $G(\boldsymbol{\delta})$ is the squared Gelbrich distance between the marginal baseline distribution of $W$ and the marginal tilted distribution of $W$ induced by $\boldsymbol{\delta}$. The manifold $\mathcal M$ is equipped with the Riemannian metric induced by the Euclidean inner product on $\mathbb{R}^d$. Global convergence of cautious Riemannian BFGS in the sense that $\liminf_{k\to\infty}\|\operatorname{grad}\psi(\boldsymbol{\delta}_k)\|=0$ follows from \citet[Theorem 4.2]{huang2018riemannian} under a compact level-set condition and Lipschitz continuous differentiability with respect to the chosen transport. We establish these properties for the marginal Gelbrich constraint by showing that the level set is a smooth embedded hypersurface, that a $C^2$ retraction and a continuous scaled transport with the pointwise norm-preserving property used in \citet{huang2015broyden,huang2018riemannian} are available, and that $\psi$ is regular on a neighbourhood containing the line-search trial points.

\paragraph{Geometry of the Gelbrich constraint.}
Let $f_W$ denote the marginal baseline law of $W$ on $\mathbb{R}^d$, and let
$$
\boldsymbol{\mu}=\mathbb E_{f_W}[W]\in\mathbb{R}^d,
\qquad
\boldsymbol{\Sigma}=\mathrm{Cov}_{f_W}(W)\in\mathbb{S}_{++}^d.
$$
For $\boldsymbol{\delta}\in\mathcal D$ (an open set on which the marginal log--moment generating function is finite), define
$$
M(\boldsymbol{\delta})=\mathbb E_{f_W}\!\left[e^{\boldsymbol{\delta}^\top W}\right],
\qquad
g_{\boldsymbol{\delta}}^{\mathrm{marg}}(w)
=\exp\!\big(\boldsymbol{\delta}^\top w-\log M(\boldsymbol{\delta})\big)\,f_W(w).
$$
Consequently, let $\boldsymbol{\mu}_{\boldsymbol{\delta}}=\mathbb E_{g_{\boldsymbol{\delta}}^{\mathrm{marg}}}[W]$ and $\boldsymbol{\Sigma}_{\boldsymbol{\delta}}=\mathrm{Cov}_{g_{\boldsymbol{\delta}}^{\mathrm{marg}}}(W)$. Equivalently,
$$
\boldsymbol{\mu}_{\boldsymbol{\delta}}=\nabla_{\boldsymbol{\delta}} \log M(\boldsymbol{\delta})\in\mathbb{R}^d,
\qquad
\boldsymbol{\Sigma}_{\boldsymbol{\delta}}=\nabla_{\boldsymbol{\delta}}^2 \log M(\boldsymbol{\delta})\in\mathbb{S}_{++}^d.
$$
The Gelbrich function is
$$
G(\boldsymbol{\delta})
:=\|\boldsymbol{\mu}_{\boldsymbol{\delta}}-\boldsymbol{\mu}\|_2^2
+\mathrm{tr}\!\Big(\boldsymbol{\Sigma}+\boldsymbol{\Sigma}_{\boldsymbol{\delta}}-2\big(\boldsymbol{\Sigma}^{1/2}\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\boldsymbol{\Sigma}^{1/2}\big)^{1/2}\Big).
$$
Equip $\mathbb{R}^d$ with the Euclidean inner product and $\mathbb{S}^d$ with the Frobenius inner product $\langle \boldsymbol{A},\boldsymbol{B}\rangle=\mathrm{tr}(\boldsymbol{A}^\top \boldsymbol{B})$.
For each $\boldsymbol{\delta}$, define the linear map $J_{\boldsymbol{\delta}}:\mathbb{R}^d\to\mathbb{S}^d$ by
$$
(J_{\boldsymbol{\delta}}\boldsymbol{e}_k)_{ij}:=\frac{\partial (\boldsymbol{\Sigma}_{\boldsymbol{\delta}})_{ij}}{\partial \delta_k},
\qquad
k=1,\dots,d,
$$
and extend by linearity so that $J_{\boldsymbol{\delta}}\boldsymbol{v}=\sum_{k=1}^d v_k J_{\boldsymbol{\delta}}\boldsymbol{e}_k$.
Let $J_{\boldsymbol{\delta}}^{\!*}:\mathbb{S}^d\to\mathbb{R}^d$ be the adjoint of $J_{\boldsymbol{\delta}}$ with respect to these inner products, that is,
$$
\langle J_{\boldsymbol{\delta}}\boldsymbol{v},\boldsymbol{H}\rangle=\boldsymbol{v}^\top\big(J_{\boldsymbol{\delta}}^{\!*}\boldsymbol{H}\big)
\qquad
(\boldsymbol{v}\in\mathbb{R}^d,\ \boldsymbol{H}\in\mathbb{S}^d),
$$
equivalently, for any $\boldsymbol{v}\in\mathbb{R}^d$,
$$
\boldsymbol{v}^\top \big(J_{\boldsymbol{\delta}}^{\!*}\boldsymbol{H}\big)
=\langle J_{\boldsymbol{\delta}} \boldsymbol{v},\boldsymbol{H}\rangle
=\mathrm{tr}\!\big((J_{\boldsymbol{\delta}} \boldsymbol{v})^\top \boldsymbol{H}\big)
=\sum_{k=1}^d v_k\, \mathrm{tr}\!\big((J_{\boldsymbol{\delta}} \boldsymbol{e}_k)^\top \boldsymbol{H}\big).
$$
Define
$$
\boldsymbol{T}_{\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\to\boldsymbol{\Sigma}}
:=\boldsymbol{\Sigma}_{\boldsymbol{\delta}}^{-1/2}\big(\boldsymbol{\Sigma}_{\boldsymbol{\delta}}^{1/2}\boldsymbol{\Sigma}\,\boldsymbol{\Sigma}_{\boldsymbol{\delta}}^{1/2}\big)^{1/2}\boldsymbol{\Sigma}_{\boldsymbol{\delta}}^{-1/2}\in \mathbb{S}_{++}^d.
$$
For $\boldsymbol{A}\in\mathbb{S}_{++}^d$, define the Lyapunov (Sylvester) operator $\mathcal L_{\boldsymbol{A}}(\boldsymbol{Y})=\boldsymbol{A}\boldsymbol{Y}+\boldsymbol{Y}\boldsymbol{A}$, and write $\mathcal L_{\boldsymbol{A}}^{-1}$ for its solution operator.

\begin{lemma}[Exact gradient and generic regularity of Gelbrich level sets]\label{lem:Gelbrich-gradient-regular}
Assume $\log M(\boldsymbol{\delta})$ is finite on a nonempty open set $\mathcal D\subset\mathbb{R}^d$. Then $\log M(\boldsymbol{\delta})$ is real--analytic on $\mathcal D$, hence so are $\boldsymbol{\mu}_{\boldsymbol{\delta}}$ and $\boldsymbol{\Sigma}_{\boldsymbol{\delta}}$.
\begin{enumerate}
\item[\textnormal{(i)}] $G$ is $C^1$ on $\mathcal D$ and
$$
\nabla G(\boldsymbol{\delta})
= 2\,\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\big(\boldsymbol{\mu}_{\boldsymbol{\delta}}-\boldsymbol{\mu}\big)
+ J_{\boldsymbol{\delta}}^{\!*}\!\Big(I- \boldsymbol{T}_{\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\to\boldsymbol{\Sigma}}\Big),
\qquad
\boldsymbol{\delta}\in\mathcal D.
$$
\item[\textnormal{(ii)}] Let $\mathcal C=\{\boldsymbol{\delta}\in\mathcal D:\nabla G(\boldsymbol{\delta})=\boldsymbol{0}\}$ and $\mathcal V=G(\mathcal C)\subset[0,\infty)$.
Then $\mathcal V$ has Lebesgue measure zero and empty interior.
In particular, for any $c>0$ with $c^2\notin\mathcal V$, the level set
$$
\mathcal M_c:=\{\boldsymbol{\delta}\in\mathcal D:\ G(\boldsymbol{\delta})=c^2\}
$$
is a $C^\infty$ (indeed real-analytic) embedded hypersurface and $\nabla G(\boldsymbol{\delta})\neq\boldsymbol{0}$ for all $\boldsymbol{\delta}\in\mathcal M_c$.
\end{enumerate}
\end{lemma}

\begin{proof}
Write $G(\boldsymbol{\delta})=G_{\mathrm{mean}}(\boldsymbol{\delta})+G_{\mathrm{cov}}(\boldsymbol{\delta})$ with
$$
G_{\mathrm{mean}}(\boldsymbol{\delta})=\|\boldsymbol{\mu}_{\boldsymbol{\delta}}-\boldsymbol{\mu}\|_2^2,
\qquad
G_{\mathrm{cov}}(\boldsymbol{\delta})=\Phi(\boldsymbol{\Sigma}_{\boldsymbol{\delta}}),
$$
where
$$
\Phi(\boldsymbol{\Theta}):=\mathrm{tr}\!\Big(\boldsymbol{\Sigma}+\boldsymbol{\Theta}-2\big(\boldsymbol{\Sigma}^{1/2}\boldsymbol{\Theta}\boldsymbol{\Sigma}^{1/2}\big)^{1/2}\Big),
\qquad \boldsymbol{\Theta}\in\mathbb{S}_{++}^d.
$$
Let $\boldsymbol{v}\in\mathbb{R}^d$ and denote the directional derivative by $D_{\boldsymbol{v}}$.
Since $\mathrm{D}\boldsymbol{\mu}_{\boldsymbol{\delta}}[\boldsymbol{v}]=\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\boldsymbol{v}$ and $\boldsymbol{\Sigma}_{\boldsymbol{\delta}}$ is symmetric,
$$
D_{\boldsymbol{v}} G_{\mathrm{mean}}(\boldsymbol{\delta})
= 2\,\langle \boldsymbol{\mu}_{\boldsymbol{\delta}}-\boldsymbol{\mu}, \boldsymbol{\Sigma}_{\boldsymbol{\delta}} \boldsymbol{v} \rangle
= 2\, \boldsymbol{v}^\top \boldsymbol{\Sigma}_{\boldsymbol{\delta}}(\boldsymbol{\mu}_{\boldsymbol{\delta}}-\boldsymbol{\mu}),
$$
hence $\nabla G_{\mathrm{mean}}(\boldsymbol{\delta})=2\,\boldsymbol{\Sigma}_{\boldsymbol{\delta}}(\boldsymbol{\mu}_{\boldsymbol{\delta}}-\boldsymbol{\mu})$.

For $\boldsymbol{H} \in \mathbb{S}^d$, the first Fréchet derivative of $\Phi$ is given by
$$
\mathrm{D}\Phi(\boldsymbol{\Theta})[\boldsymbol{H}] = \langle I - \boldsymbol{T}_{\boldsymbol{\Theta}\to\boldsymbol{\Sigma}}, \boldsymbol{H} \rangle,
$$
where $\boldsymbol{T}_{\boldsymbol{\Theta}\to\boldsymbol{\Sigma}} := \boldsymbol{\Theta}^{-1/2}(\boldsymbol{\Theta}^{1/2}\boldsymbol{\Sigma}\boldsymbol{\Theta}^{1/2})^{1/2}\boldsymbol{\Theta}^{-1/2}$. This follows from the Fréchet derivative of the principal matrix square root, $\mathrm{D}(\boldsymbol{A}^{1/2})[\boldsymbol{V}] = \mathcal{L}_{\boldsymbol{A}^{1/2}}^{-1}(\boldsymbol{V})$ \citep[Eqs.~(14)--(16)]{malago2018wasserstein}. In particular, for $\boldsymbol{A}\in\mathbb{S}_{++}^d$ and $\boldsymbol{V}\in\mathbb{S}^d$,
$$
\mathrm{D}\,\mathrm{tr}(\boldsymbol{A}^{1/2})[\boldsymbol{V}]
=\tfrac12\,\mathrm{tr}(\boldsymbol{A}^{-1/2}\boldsymbol{V}).
$$
With $\boldsymbol{A}=\boldsymbol{\Sigma}^{1/2}\boldsymbol{\Theta}\boldsymbol{\Sigma}^{1/2}$ and $\boldsymbol{V}=\boldsymbol{\Sigma}^{1/2}\boldsymbol{H}\boldsymbol{\Sigma}^{1/2}$,
$$
\mathrm{D}\Phi(\boldsymbol{\Theta})[\boldsymbol{H}]
=\mathrm{tr}(\boldsymbol{H})
-\mathrm{tr}\!\Big(\boldsymbol{\Sigma}^{1/2}\boldsymbol{A}^{-1/2}\boldsymbol{\Sigma}^{1/2}\boldsymbol{H}\Big)
=\langle I-\boldsymbol{T}_{\boldsymbol{\Theta}\to\boldsymbol{\Sigma}},\,\boldsymbol{H}\rangle.
$$
By the chain rule and the definition of $J_{\boldsymbol{\delta}}$,
$$
D_{\boldsymbol{v}} G_{\mathrm{cov}}(\boldsymbol{\delta})
= \mathrm{D}\Phi(\boldsymbol{\Sigma}_{\boldsymbol{\delta}})\!\big[J_{\boldsymbol{\delta}} \boldsymbol{v}\big]
= \langle \,I-\boldsymbol{T}_{\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\to\boldsymbol{\Sigma}}\, , J_{\boldsymbol{\delta}} \boldsymbol{v} \rangle
= \boldsymbol{v}^\top J_{\boldsymbol{\delta}}^{\!*}\!\big(I-\boldsymbol{T}_{\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\to\boldsymbol{\Sigma}}\big),
$$
which implies $\nabla G_{\mathrm{cov}}(\boldsymbol{\delta})=J_{\boldsymbol{\delta}}^{\!*}\!\big(I-\boldsymbol{T}_{\boldsymbol{\Sigma}_{\boldsymbol{\delta}}\to\boldsymbol{\Sigma}}\big)$.
Summing these terms yields the gradient in (i).

For part (ii), $\log M(\boldsymbol{\delta})$ is real--analytic on $\mathcal D$, hence so are $\boldsymbol{\mu}_{\boldsymbol{\delta}}$ and $\boldsymbol{\Sigma}_{\boldsymbol{\delta}}$, and therefore $G$ is $C^1$ on $\mathcal D$.
Since $G$ is real--analytic on $\mathcal D$, it is $C^\infty$ on $\mathcal D$, and Sard's theorem yields that the set of critical values $\mathcal V$ has Lebesgue measure zero.
Since $\mathcal V$ has Lebesgue measure zero, it has empty interior.
For any $c>0$ with $c^2\notin\mathcal V$, every $\boldsymbol{\delta}\in\mathcal M_c$ satisfies $\nabla G(\boldsymbol{\delta})\neq\boldsymbol{0}$; the regular level--set theorem yields that $\mathcal M_c$ is a $C^\infty$ (indeed real-analytic) embedded hypersurface.
\end{proof}

\paragraph{Projection retraction and scaled vector transport.}
Fix $c>0$ such that $c^2\notin\mathcal V$ and write $\mathcal M_c=\{\boldsymbol{\delta}\in\mathcal D:\,G(\boldsymbol{\delta})=c^2\}$. For $\boldsymbol{\delta}\in\mathcal M_c$, let $\boldsymbol{n}(\boldsymbol{\delta}):={\nabla G(\boldsymbol{\delta})}/{\|\nabla G(\boldsymbol{\delta})\|}$ be the unit normal vector and denote the orthogonal projection onto the tangent space $T_{\boldsymbol{\delta}}\mathcal M_c$ by
$$
P_{\boldsymbol{\delta}} := I - \boldsymbol{n}(\boldsymbol{\delta})\boldsymbol{n}(\boldsymbol{\delta})^\top.
$$

Let $\Pi:\mathcal N\to\mathcal M_c$ be the orthogonal projection from a tubular neighbourhood $\mathcal N$ of $\mathcal M_c$.
For $\boldsymbol{\delta}\in\mathcal M_c$, define the retraction $R_{\boldsymbol{\delta}}$ on a sufficiently small ball $\mathcal B_{\boldsymbol{\delta}}\subset T_{\boldsymbol{\delta}}\mathcal M_c$ by
$$
R_{\boldsymbol{\delta}}(\boldsymbol{\xi}):=\Pi(\boldsymbol{\delta}+\boldsymbol{\xi}),
\qquad
\boldsymbol{\xi}\in\mathcal B_{\boldsymbol{\delta}}.
$$
Define the differentiated-retraction transport
$$
T^{R}_{\boldsymbol{\delta},\boldsymbol{\xi}}(\boldsymbol{\zeta})
:= \mathrm{D}R_{\boldsymbol{\delta}}(\boldsymbol{\xi})[\boldsymbol{\zeta}],
\qquad
\boldsymbol{\zeta}\in T_{\boldsymbol{\delta}}\mathcal M_c.
$$
Following \citet[Eq.~(4.3)]{huang2015broyden}, define the scaled transport
$$
T^{S}_{\boldsymbol{\delta},\boldsymbol{\xi}}(\boldsymbol{\zeta})
:=
\begin{cases}
\dfrac{\|\boldsymbol{\zeta}\|}{\|T^{R}_{\boldsymbol{\delta},\boldsymbol{\xi}}(\boldsymbol{\zeta})\|}\,T^{R}_{\boldsymbol{\delta},\boldsymbol{\xi}}(\boldsymbol{\zeta}), & \boldsymbol{\zeta}\neq \boldsymbol{0},\\[6pt]
\boldsymbol{0}, & \boldsymbol{\zeta}=\boldsymbol{0},
\end{cases}
$$
which is norm-preserving and satisfies the requirements (2.5)--(2.8) therein.
For a step $\boldsymbol{\xi}\in T_{\boldsymbol{\delta}}\mathcal M_c$ and $\boldsymbol{\delta}_+:=R_{\boldsymbol{\delta}}(\boldsymbol{\xi})$, define
$$
\mathcal T_{\boldsymbol{\delta}\to\boldsymbol{\delta}_+}(\boldsymbol{\zeta})
:=T^{S}_{\boldsymbol{\delta},\boldsymbol{\xi}}(\boldsymbol{\zeta}),
\qquad
\boldsymbol{\zeta}\in T_{\boldsymbol{\delta}}\mathcal M_c.
$$

\begin{lemma}[Validity of transport]\label{lem:validity-transport}
The retraction $R$ and the transport $\mathcal T$ defined above satisfy:
\begin{enumerate}
\item[\textnormal{(a)}] there exists an open neighbourhood $\mathcal U\subset T\mathcal M_c$ of the zero section such that $R_{\boldsymbol{\delta}}$ and $\mathcal T_{\boldsymbol{\delta}\to R_{\boldsymbol{\delta}}(\boldsymbol{\xi})}$ are well defined for $(\boldsymbol{\delta},\boldsymbol{\xi})\in\mathcal U$ and are $C^0$ in all arguments;
\item[\textnormal{(b)}] $R_{\boldsymbol{\delta}}(\boldsymbol{0})=\boldsymbol{\delta}$ and $\mathrm{D}R_{\boldsymbol{\delta}}(\boldsymbol{0})=\mathrm{Id}_{T_{\boldsymbol{\delta}}\mathcal M_c}$, and for every $\boldsymbol{\zeta}\in T_{\boldsymbol{\delta}}\mathcal M_c$,
$$
\mathcal T_{\boldsymbol{\delta}\to R_{\boldsymbol{\delta}}(\boldsymbol{\xi})}(\boldsymbol{\zeta})
= T^{R}_{\boldsymbol{\delta},\boldsymbol{\xi}}(\boldsymbol{\zeta}) + O(\|\boldsymbol{\xi}\|\,\|\boldsymbol{\zeta}\|) \quad (\boldsymbol{\xi}\to \boldsymbol{0}),
$$
and in particular $T^{R}_{\boldsymbol{\delta},\boldsymbol{0}}=\mathrm{Id}_{T_{\boldsymbol{\delta}}\mathcal M_c}$;
\item[\textnormal{(c)}] for every $\boldsymbol{\delta}\in\mathcal M_c$ and $\boldsymbol{\xi}\in\mathcal B_{\boldsymbol{\delta}}$,
$$
\|\mathcal T_{\boldsymbol{\delta}\to R_{\boldsymbol{\delta}}(\boldsymbol{\xi})}(\boldsymbol{\zeta})\|
=\|\boldsymbol{\zeta}\|
\qquad
(\boldsymbol{\zeta}\in T_{\boldsymbol{\delta}}\mathcal M_c),
$$
so for each fixed $(\boldsymbol{\delta},\boldsymbol{\xi})$, the map
$\boldsymbol{\zeta}\mapsto \mathcal T_{\boldsymbol{\delta}\to R_{\boldsymbol{\delta}}(\boldsymbol{\xi})}(\boldsymbol{\zeta})$
is pointwise norm-preserving on $T_{\boldsymbol{\delta}}\mathcal M_c$, and $\mathcal T$ is uniformly bounded on compact subsets of $\mathcal M_c$ in the sense that
$$
\|\mathcal T_{\boldsymbol{\delta}\to R_{\boldsymbol{\delta}}(\boldsymbol{\xi})}(\boldsymbol{\zeta})\|\le \|\boldsymbol{\zeta}\|
$$
for all admissible $(\boldsymbol{\delta},\boldsymbol{\xi},\boldsymbol{\zeta})$.
\end{enumerate}
\end{lemma}

\begin{proof}
Property (a) follows from the tubular neighbourhood theorem and the $C^1$ smoothness of $\Pi$:
$R_{\boldsymbol{\delta}}(\boldsymbol{\xi})=\Pi(\boldsymbol{\delta}+\boldsymbol{\xi})$ is well defined and $C^1$ for $\boldsymbol{\xi}$ small, and $\mathrm{D}R_{\boldsymbol{\delta}}(\boldsymbol{\xi})$ is a linear map between tangent spaces for $\|\boldsymbol{\xi}\|$ sufficiently small.
The scaled transport $T^S$ satisfies the continuity and first-order conditions invoked in \citet{huang2015broyden}, so $\mathcal T$ is continuous in all arguments.

For (b), $\Pi(\boldsymbol{\delta})=\boldsymbol{\delta}$ and $\mathrm{D}\Pi(\boldsymbol{\delta})=P_{\boldsymbol{\delta}}$, hence $R_{\boldsymbol{\delta}}(\boldsymbol{0})=\boldsymbol{\delta}$ and $\mathrm{D}R_{\boldsymbol{\delta}}(\boldsymbol{0})=P_{\boldsymbol{\delta}}$.
Since $P_{\boldsymbol{\delta}}$ is the identity on $T_{\boldsymbol{\delta}}\mathcal M_c$, $\mathrm{D}R_{\boldsymbol{\delta}}(\boldsymbol{0})=\mathrm{Id}_{T_{\boldsymbol{\delta}}\mathcal M_c}$.
The first--order agreement between $\mathcal T$ and $\mathrm{D}R_{\boldsymbol{\delta}}(\boldsymbol{0})$ follows from \citet[(2.5)--(2.7), Lem.~3.5]{huang2015broyden}.

For (c), by construction,
$$
\|T^{S}_{\boldsymbol{\delta},\boldsymbol{\xi}}(\boldsymbol{\zeta})\|
=\|\boldsymbol{\zeta}\|
\qquad
(\boldsymbol{\zeta}\in T_{\boldsymbol{\delta}}\mathcal M_c),
$$
so $\mathcal T_{\boldsymbol{\delta}\to R_{\boldsymbol{\delta}}(\boldsymbol{\xi})}=T^S_{\boldsymbol{\delta},\boldsymbol{\xi}}$ is pointwise norm-preserving:
$$
\|\mathcal T_{\boldsymbol{\delta}\to R_{\boldsymbol{\delta}}(\boldsymbol{\xi})}(\boldsymbol{\zeta})\|=\|\boldsymbol{\zeta}\|
\qquad
(\boldsymbol{\zeta}\in T_{\boldsymbol{\delta}}\mathcal M_c).
$$
The stated uniform boundedness on compact subsets then follows with constant $1$.
\end{proof}


\paragraph{Objective regularity for the global target.}
For $\boldsymbol{x}\in\mathcal X$ and $\boldsymbol{\delta}\in U$, define the local tilted conditional mean
$$
\eta_{\boldsymbol{\delta}}(\boldsymbol{x})
:= \mathbb E_f[\mu(\boldsymbol{x},W)e^{\boldsymbol{\delta}^\top W}\mid X=\boldsymbol{x}],
\qquad
\nu_{\boldsymbol{\delta}}(\boldsymbol{x})
:= \mathbb E_f[e^{\boldsymbol{\delta}^\top W}\mid X=\boldsymbol{x}],
$$
$$
m_{\boldsymbol{\delta}}(\boldsymbol{x})
:= \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{x})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})},
\qquad
\psi(\boldsymbol{\delta})
:= \mathbb E\big\{m_{\boldsymbol{\delta}}(X)\big\}.
$$

\begin{lemma}[Conditional regularity of the local tilted mean]\label{lem:conditional-regularity-local-tilted-mean}
Assume $|\mu(x,w)|\le C(1+\|w\|^p)$ for some finite constants $C,p>0$.
Let $U\subset\mathbb{R}^d$ be open and let $K\subset U$ be compact.
Assume
\begin{equation}\label{eq:conditional-envelope-regularity}
A(X):=\sup_{\boldsymbol{\delta}\in U}\mathbb E_f\!\big[e^{\boldsymbol{\delta}^\top W}(1+\|W\|^{p+2})\mid X\big]<\infty
\quad\text{a.s.},
\qquad
\mathbb E\big[A(X)^2\big]<\infty,
\end{equation}
and
\begin{equation}\label{eq:conditional-denominator-lower-bound}
\inf_{\boldsymbol{\delta}\in K}\nu_{\boldsymbol{\delta}}(X)\ge D_{\min}>0
\quad\text{a.s.}
\end{equation}
Then for almost every $X$, the map $\boldsymbol{\delta}\mapsto m_{\boldsymbol{\delta}}(X)$ is $C^2$ on $K$.
Moreover, there exist finite constants $C_0,C_1,C_2$, depending only on $C$, $p$, and $D_{\min}$, such that with
$$
B_j(X):=C_j\{1+A(X)+A(X)^2\},
\qquad j=0,1,2,
$$
we have almost surely
$$
\sup_{\boldsymbol{\delta}\in K}|m_{\boldsymbol{\delta}}(X)|\le B_0(X),
\qquad
\sup_{\boldsymbol{\delta}\in K}\|\nabla m_{\boldsymbol{\delta}}(X)\|\le B_1(X),
\qquad
\sup_{\boldsymbol{\delta}\in K}\|\nabla^2 m_{\boldsymbol{\delta}}(X)\|\le B_2(X),
$$
and $\mathbb E[B_j(X)]<\infty$ for $j=0,1,2$.
\end{lemma}

\begin{proof}
Fix $\boldsymbol{\delta}\in U$.
By \eqref{eq:conditional-envelope-regularity}, the maps $\eta_{\boldsymbol{\delta}}(X)$ and $\nu_{\boldsymbol{\delta}}(X)$ are well defined almost surely, and differentiation under the conditional expectation is justified up to second order because $e^{\boldsymbol{\delta}^\top W}(1+\|W\|^{p+2})$ dominates the first- and second-order directional derivatives of both integrands.
Thus, for almost every $X$,
$$
\nabla \eta_{\boldsymbol{\delta}}(X)=\mathbb E_f[\mu(X,W)We^{\boldsymbol{\delta}^\top W}\mid X],
\qquad
\nabla^2 \eta_{\boldsymbol{\delta}}(X)=\mathbb E_f[\mu(X,W)WW^\top e^{\boldsymbol{\delta}^\top W}\mid X],
$$
$$
\nabla \nu_{\boldsymbol{\delta}}(X)=\mathbb E_f[We^{\boldsymbol{\delta}^\top W}\mid X],
\qquad
\nabla^2 \nu_{\boldsymbol{\delta}}(X)=\mathbb E_f[WW^\top e^{\boldsymbol{\delta}^\top W}\mid X].
$$
The polynomial growth bound on $\mu$ implies that there is a finite constant $C_\eta$, depending only on $C$ and $p$, such that almost surely
$$
\sup_{\boldsymbol{\delta}\in K}\Big(
|\eta_{\boldsymbol{\delta}}(X)|+
\|\nabla \eta_{\boldsymbol{\delta}}(X)\|+
\|\nabla^2 \eta_{\boldsymbol{\delta}}(X)\|+
|\nu_{\boldsymbol{\delta}}(X)|+
\|\nabla \nu_{\boldsymbol{\delta}}(X)\|+
\|\nabla^2 \nu_{\boldsymbol{\delta}}(X)\|
\Big)
\le C_\eta A(X).
$$
By \eqref{eq:conditional-denominator-lower-bound}, the quotient rule gives, for almost every $X$,
$$
\nabla m_{\boldsymbol{\delta}}(X)
=\frac{\nabla\eta_{\boldsymbol{\delta}}(X)}{\nu_{\boldsymbol{\delta}}(X)}
-\frac{\eta_{\boldsymbol{\delta}}(X)\nabla\nu_{\boldsymbol{\delta}}(X)}{\nu_{\boldsymbol{\delta}}(X)^2},
$$
$$
\nabla^2 m_{\boldsymbol{\delta}}(X)
=\frac{\nabla^2\eta_{\boldsymbol{\delta}}(X)}{\nu_{\boldsymbol{\delta}}(X)}
-\frac{\nabla\eta_{\boldsymbol{\delta}}(X)\nabla\nu_{\boldsymbol{\delta}}(X)^\top + \nabla\nu_{\boldsymbol{\delta}}(X)\nabla\eta_{\boldsymbol{\delta}}(X)^\top + \eta_{\boldsymbol{\delta}}(X)\nabla^2\nu_{\boldsymbol{\delta}}(X)}{\nu_{\boldsymbol{\delta}}(X)^2}
+\frac{2\eta_{\boldsymbol{\delta}}(X)\nabla\nu_{\boldsymbol{\delta}}(X)\nabla\nu_{\boldsymbol{\delta}}(X)^\top}{\nu_{\boldsymbol{\delta}}(X)^3}.
$$
Therefore there exist finite constants $C_0,C_1,C_2$, depending only on $C$, $p$, and $D_{\min}$, such that
$$
\sup_{\boldsymbol{\delta}\in K}|m_{\boldsymbol{\delta}}(X)|\le C_0\{1+A(X)\},
\qquad
\sup_{\boldsymbol{\delta}\in K}\|\nabla m_{\boldsymbol{\delta}}(X)\|\le C_1\{1+A(X)+A(X)^2\},
$$
$$
\sup_{\boldsymbol{\delta}\in K}\|\nabla^2 m_{\boldsymbol{\delta}}(X)\|\le C_2\{1+A(X)+A(X)^2\}
\qquad\text{a.s.}
$$
Since $\mathbb E[A(X)^2]<\infty$, the envelopes $B_j(X)=C_j\{1+A(X)+A(X)^2\}$ are integrable.
This proves the claim.
\end{proof}

\begin{corollary}[Objective regularity and line search on Gelbrich level sets]\label{lem:regularity-linesearch}
Let $c>0$ satisfy $c^2\notin\mathcal V$ and set $\mathcal M=\{\boldsymbol{\delta}\in\mathbb{R}^d:\,G(\boldsymbol{\delta})=c^2\}$.
Assume the boundary-separation condition
\begin{equation}\label{eq:boundary-separation}
G^-_\infty:=\liminf_{\|\boldsymbol{\delta}\|\to\infty,\ \boldsymbol{\delta}\in\mathcal D} G(\boldsymbol{\delta}) > c^2.
\end{equation}
Choose $R_c>0$ such that
\begin{equation}\label{eq:levelset-radius-bound}
G(\boldsymbol{\delta})>c^2
\qquad
(\boldsymbol{\delta}\in\mathcal D,\ \|\boldsymbol{\delta}\|\ge R_c),
\end{equation}
and define $K_c:=\overline B(\boldsymbol{0},R_c)$.
Let $R$ and $\mathcal T$ be as defined above, and let the Riemannian metric be the Euclidean metric on $T_{\boldsymbol{\delta}}\mathcal M$.
Assume the conditions of Lemma~\ref{lem:conditional-regularity-local-tilted-mean} on an open neighbourhood $U$ of $K_c$.
Assume also the constraint regularity on $U$:
\begin{equation}\label{eq:constraint-regular}
\inf_{\boldsymbol{\delta}\in U\cap\mathcal M}\|\nabla G(\boldsymbol{\delta})\| \ge \epsilon_{\nabla}>0,
\qquad
\sup_{\boldsymbol{\delta}\in U}\|\nabla^2 G(\boldsymbol{\delta})\|\le M_G<\infty.
\end{equation}
Then $\mathcal M$ is compact, and:
\begin{enumerate}
\item[\textnormal{(a)}] $\psi$ is $C^2$ on $K_c$, with
$$
\nabla\psi(\boldsymbol{\delta})=\mathbb E\big[\nabla m_{\boldsymbol{\delta}}(X)\big],
\qquad
\nabla^2\psi(\boldsymbol{\delta})=\mathbb E\big[\nabla^2 m_{\boldsymbol{\delta}}(X)\big],
$$
and
$$
\sup_{\boldsymbol{\delta}\in K_c}\|\nabla^2\psi(\boldsymbol{\delta})\|\le M_\psi<\infty.
$$
Consequently, $\nabla\psi$ is $M_\psi$--Lipschitz on $K_c$.
\item[\textnormal{(b)}] Writing $\boldsymbol{n}(\boldsymbol{\delta})=\nabla G(\boldsymbol{\delta})/\|\nabla G(\boldsymbol{\delta})\|$ and $P(\boldsymbol{\delta})=I-\boldsymbol{n}(\boldsymbol{\delta})\boldsymbol{n}(\boldsymbol{\delta})^\top$, the Riemannian gradient $\operatorname{grad}\psi(\boldsymbol{\delta})=P(\boldsymbol{\delta})\nabla\psi(\boldsymbol{\delta})$ is Lipschitz on $\mathcal M$, that is, there exists $L>0$ such that
$$
\|\operatorname{grad}\psi(\boldsymbol{\delta})-\operatorname{grad}\psi(\boldsymbol{\delta}')\|
\le L\|\boldsymbol{\delta}-\boldsymbol{\delta}'\|
\qquad
(\boldsymbol{\delta},\boldsymbol{\delta}'\in \mathcal M).
$$
\item[\textnormal{(c)}] Fix $0<c_1<c_2<1$.
For any $\boldsymbol{\delta}\in \mathcal M$ and any descent direction $\boldsymbol{\eta}\in T_{\boldsymbol{\delta}}\mathcal M$ with $\langle \operatorname{grad}\psi(\boldsymbol{\delta}), \boldsymbol{\eta} \rangle<0$, there exists a step size $t_\ast>0$ in the domain of $\gamma(t)=R_{\boldsymbol{\delta}}(t\boldsymbol{\eta})$ such that $\gamma$ satisfies the weak Wolfe conditions at $t_\ast$.
\end{enumerate}
\end{corollary}

\begin{proof}
By \eqref{eq:levelset-radius-bound}, every point of $\mathcal M$ lies in $K_c$.
Since $G$ is continuous on $U$ and $K_c\subset U$, the set
$$
\mathcal M = K_c\cap G^{-1}(\{c^2\})
$$
is closed in the compact set $K_c$.
Hence $\mathcal M$ is compact.

For part (a), Lemma~\ref{lem:conditional-regularity-local-tilted-mean} provides an integrable envelope $B_2(X)$ such that
$$
\sup_{\boldsymbol{\delta}\in K_c}\|\nabla^2 m_{\boldsymbol{\delta}}(X)\|\le B_2(X)
\qquad\text{a.s.}
$$
The same lemma yields analogous integrable envelopes for $m_{\boldsymbol{\delta}}(X)$ and $\nabla m_{\boldsymbol{\delta}}(X)$.
Hence dominated differentiation applies to
$$
\psi(\boldsymbol{\delta})=\mathbb E\big\{m_{\boldsymbol{\delta}}(X)\big\},
$$
which gives
$$
\nabla\psi(\boldsymbol{\delta})=\mathbb E\big[\nabla m_{\boldsymbol{\delta}}(X)\big],
\qquad
\nabla^2\psi(\boldsymbol{\delta})=\mathbb E\big[\nabla^2 m_{\boldsymbol{\delta}}(X)\big].
$$
Therefore
$$
\sup_{\boldsymbol{\delta}\in K_c}\|\nabla^2\psi(\boldsymbol{\delta})\|
\le \mathbb E\Big[\sup_{\boldsymbol{\delta}\in K_c}\|\nabla^2 m_{\boldsymbol{\delta}}(X)\|\Big]
\le \mathbb E\big[B_2(X)\big]
=:M_\psi<\infty.
$$
The Lipschitz property of $\nabla\psi$ on $K_c$ follows from the mean value theorem.

For $\boldsymbol{\delta},\boldsymbol{\delta}'\in \mathcal M$,
$$
\operatorname{grad}\psi(\boldsymbol{\delta})-\operatorname{grad}\psi(\boldsymbol{\delta}')
=P(\boldsymbol{\delta})\big(\nabla\psi(\boldsymbol{\delta})-\nabla\psi(\boldsymbol{\delta}')\big)
+\big(P(\boldsymbol{\delta})-P(\boldsymbol{\delta}')\big)\nabla\psi(\boldsymbol{\delta}').
$$
Since $\|P(\boldsymbol{\delta})\|_{\mathrm{op}}\le 1$,
$$
\|P(\boldsymbol{\delta})\big(\nabla\psi(\boldsymbol{\delta})-\nabla\psi(\boldsymbol{\delta}')\big)\|
\le M_\psi\|\boldsymbol{\delta}-\boldsymbol{\delta}'\|.
$$
Let $\boldsymbol{n}(\boldsymbol{\delta})=\nabla G(\boldsymbol{\delta})/\|\nabla G(\boldsymbol{\delta})\|$.
By \eqref{eq:constraint-regular}, $\|\nabla G(\boldsymbol{\delta})\|\ge\epsilon_{\nabla}$ on $\mathcal M$, and $\|\nabla G(\boldsymbol{\delta})-\nabla G(\boldsymbol{\delta}')\|\le M_G\|\boldsymbol{\delta}-\boldsymbol{\delta}'\|$ on $K_c$.
Using
$$
\boldsymbol{n}(\boldsymbol{\delta})-\boldsymbol{n}(\boldsymbol{\delta}')
=\frac{\nabla G(\boldsymbol{\delta})-\nabla G(\boldsymbol{\delta}')}{\|\nabla G(\boldsymbol{\delta})\|}
+\Big(\frac{1}{\|\nabla G(\boldsymbol{\delta})\|}-\frac{1}{\|\nabla G(\boldsymbol{\delta}')\|}\Big)\nabla G(\boldsymbol{\delta}'),
$$
one obtains
$$
\|\boldsymbol{n}(\boldsymbol{\delta})-\boldsymbol{n}(\boldsymbol{\delta}')\|
\le \frac{2}{\epsilon_{\nabla}}\,\|\nabla G(\boldsymbol{\delta})-\nabla G(\boldsymbol{\delta}')\|
\le \frac{2M_G}{\epsilon_{\nabla}}\,\|\boldsymbol{\delta}-\boldsymbol{\delta}'\|.
$$
Since $P(\boldsymbol{\delta})=I-\boldsymbol{n}(\boldsymbol{\delta})\boldsymbol{n}(\boldsymbol{\delta})^\top$,
$$
\|P(\boldsymbol{\delta})-P(\boldsymbol{\delta}')\|
\le \|\boldsymbol{n}(\boldsymbol{\delta})-\boldsymbol{n}(\boldsymbol{\delta}')\|\big(\|\boldsymbol{n}(\boldsymbol{\delta})\|+\|\boldsymbol{n}(\boldsymbol{\delta}')\|\big)
\le \frac{4M_G}{\epsilon_{\nabla}}\,\|\boldsymbol{\delta}-\boldsymbol{\delta}'\|.
$$
Let $M_1=\sup_{\boldsymbol{\delta}\in K_c}\|\nabla\psi(\boldsymbol{\delta})\|<\infty$.
Combining these bounds yields
$$
\|\operatorname{grad}\psi(\boldsymbol{\delta})-\operatorname{grad}\psi(\boldsymbol{\delta}')\|
\le \Big(M_\psi+\frac{4M_G}{\epsilon_{\nabla}}M_1\Big)\,\|\boldsymbol{\delta}-\boldsymbol{\delta}'\|,
$$
so part (b) holds with $L=M_\psi+(4M_G/\epsilon_{\nabla})M_1$.

For part (c), define the one-dimensional line-search function $h(t)=\psi(R_{\boldsymbol{\delta}}(t\boldsymbol{\eta}))$.
By part (a) and the $C^1$ regularity of $R$, the map $h$ is continuously differentiable on an interval containing $0$.
Because $R_{\boldsymbol{\delta}}(t\boldsymbol{\eta})\in \mathcal M$ whenever the retraction is defined, and because $\psi$ is continuous on the compact set $\mathcal M$, the function $h$ is bounded below on its domain.
Therefore there exists $t_\ast>0$ satisfying the weak Wolfe conditions along $\gamma(t)=R_{\boldsymbol{\delta}}(t\boldsymbol{\eta})$; see \citet[Proposition 1]{ring2012optimization}.
\end{proof}

For an accepted step $t_\ast$, define
$$
\boldsymbol{s}:=\mathcal T_{\boldsymbol{\delta}\to\boldsymbol{\delta}_+}(t_\ast\boldsymbol{\eta}),
\qquad
\boldsymbol{y}:=\operatorname{grad}\psi(\boldsymbol{\delta}_+)-\mathcal T_{\boldsymbol{\delta}\to\boldsymbol{\delta}_+}\big(\operatorname{grad}\psi(\boldsymbol{\delta})\big),
\qquad
\boldsymbol{\delta}_+:=R_{\boldsymbol{\delta}}(t_\ast\boldsymbol{\eta}).
$$
The cautious RBFGS update of \citet[Algorithm 1]{huang2018riemannian} is then applied whenever the prescribed curvature condition holds; otherwise the current approximation is transported to the new tangent space without updating the Hessian surrogate.

\begin{lemma}[Feasible initialization and containment]\label{lem:containment}
Let $c>0$ satisfy $c^2\notin\mathcal V$ and set $\mathcal M=\{\boldsymbol{\delta}:G(\boldsymbol{\delta})=c^2\}$.
Assume the boundary-separation condition \eqref{eq:boundary-separation}.
Assume that $G$ satisfies the local quadratic control near the origin: there exist $\rho>0$, $\varepsilon\in(0,1)$ and a symmetric positive--definite matrix $\boldsymbol{H}_G(\boldsymbol{0})$ with eigenvalues $\lambda_{\min},\lambda_{\max}>0$ such that, for all $\|\boldsymbol{\delta}\|\le\rho$,
\begin{equation}\label{eq:local-quadratic-G}
\tfrac12(1-\varepsilon)\lambda_{\min}\|\,\boldsymbol{\delta}\|^2
\ \le\ G(\boldsymbol{\delta})\ \le\ \tfrac12(1+\varepsilon)\lambda_{\max}\|\,\boldsymbol{\delta}\|^2.
\end{equation}
Assume also the hypotheses of Corollary~\ref{lem:regularity-linesearch}.
\begin{enumerate}
\item[\textnormal{(i)}] For every prescribed local radius $r_0\in(0,\rho]$, there exists $c_0>0$ such that for any $c\in(0,c_0)$ one can select a unit vector $\boldsymbol{v}$ and $t^\ast\in(0,r_0]$ with $G(t^\ast \boldsymbol{v})=c^2$ and $\boldsymbol{\delta}_0:=t^\ast \boldsymbol{v}\in \mathcal M\cap \overline B(\boldsymbol{0},r_0)$.
\item[\textnormal{(ii)}] Let $\mathcal L=\{\boldsymbol{\delta}\in \mathcal M:\ \psi(\boldsymbol{\delta})\le \psi(\boldsymbol{\delta}_0)\}$.
Then $\mathcal M$ is compact, $\mathcal L$ is compact, and for any sequence $\{\boldsymbol{\delta}_k\}$ generated by Riemannian BFGS on $\mathcal M$ using $R$ and $\mathcal T$ above with a weak Wolfe line search, one has $\psi(\boldsymbol{\delta}_{k+1})\le \psi(\boldsymbol{\delta}_k)\le \psi(\boldsymbol{\delta}_0)$ and hence $\boldsymbol{\delta}_k\in \mathcal L$ for all $k\ge0$.
\end{enumerate}
\end{lemma}

\begin{proof}
For part (i), fix $r_0\in(0,\rho]$.
Fix a unit vector $\boldsymbol{v}$ and define $q(t)=G(t\boldsymbol{v})$ on $[0,r_0]$.
Then $q$ is continuous, $q(0)=0$, and by \eqref{eq:local-quadratic-G},
$$
\tfrac12(1-\varepsilon)\lambda_{\min}t^2 \ \le\ q(t)\ \le\ \tfrac12(1+\varepsilon)\lambda_{\max}t^2
\qquad
(0\le t\le r_0).
$$
Let $c_0=\sqrt{\tfrac12(1-\varepsilon)\lambda_{\min}}\,r_0$.
For any $c\in(0,c_0)$, there exists $t^\ast\in(0,r_0]$ with $q(t^\ast)=c^2$ by the intermediate value theorem.
Then $\boldsymbol{\delta}_0=t^\ast\boldsymbol{v}\in \mathcal M\cap \overline B(\boldsymbol{0},r_0)$, proving part (i).

For part (ii), condition \eqref{eq:boundary-separation} implies the existence of $R_c>0$ such that $G(\boldsymbol{\delta})>c^2$ for all $\boldsymbol{\delta}\in\mathcal D$ with $\|\boldsymbol{\delta}\|\ge R_c$.
Hence $\mathcal M\subset \overline B(\boldsymbol{0},R_c)$.
By Corollary~\ref{lem:regularity-linesearch}, the level set $\mathcal M$ is compact and $\psi$ is continuous on $\mathcal M$.
Hence $\mathcal L$ is a closed subset of the compact set $\mathcal M$, so $\mathcal L$ is compact.
Now proceed by induction.
Assume $\boldsymbol{\delta}_k\in \mathcal L$ and let $\boldsymbol{\eta}_k\in T_{\boldsymbol{\delta}_k}\mathcal M$ be the search direction.
Let $\alpha_k>0$ be produced by the weak Wolfe line search applied to $\gamma(t)=R_{\boldsymbol{\delta}_k}(t\boldsymbol{\eta}_k)$ and set $\boldsymbol{\delta}_{k+1}=R_{\boldsymbol{\delta}_k}(\alpha_k\boldsymbol{\eta}_k)$.
The Armijo condition yields
$$
\psi(\boldsymbol{\delta}_{k+1})\ \le\ \psi(\boldsymbol{\delta}_k)+c_1\alpha_k\,\langle \operatorname{grad}\psi(\boldsymbol{\delta}_k), \boldsymbol{\eta}_k \rangle
\ <\ \psi(\boldsymbol{\delta}_k)\ \le\ \psi(\boldsymbol{\delta}_0),
$$
hence $\boldsymbol{\delta}_{k+1}\in \mathcal L$.
Therefore $\psi(\boldsymbol{\delta}_{k+1})\le \psi(\boldsymbol{\delta}_k)\le \psi(\boldsymbol{\delta}_0)$ and $\boldsymbol{\delta}_k\in \mathcal L$ for all $k\ge0$.
\end{proof}

\paragraph{Stationarity conclusion.}
Under \eqref{eq:boundary-separation}, Lemma~\ref{lem:containment} shows that the initial sublevel set $\mathcal L=\{\boldsymbol{\delta}\in \mathcal M:\psi(\boldsymbol{\delta})\le \psi(\boldsymbol{\delta}_0)\}$ is compact.
Thus Assumption 4.1 in \citet{huang2018riemannian} is satisfied for the RBFGS iterates started at $\boldsymbol{\delta}_0$.
Together with Assumption 4.2, applied here with the scaled transport $\mathcal T$ above, Theorem 4.2 yields
$$
\liminf_{k\to\infty}\|\operatorname{grad}\psi(\boldsymbol{\delta}_k)\|=0.
$$
Since $\{\boldsymbol{\delta}_k\}\subset \mathcal L$ and $\mathcal L$ is compact, the sequence admits an accumulation point $\boldsymbol{\delta}_\star$.
Continuity of $\operatorname{grad}\psi$ implies that any accumulation point along a subsequence with $\|\operatorname{grad}\psi(\boldsymbol{\delta}_{k_j})\|\to 0$ is Riemannian stationary.



\section{Detailed Proof for Minimax Lower Bound}

\subsection*{Standing Assumptions and Notation}

Let $\boldsymbol{Z}=(\boldsymbol{X},\boldsymbol{W},Y)$ with $\boldsymbol{X}\in\mathbb R^p$, $\boldsymbol{W}\in\mathbb R^q$, and $Y\in\mathbb R$.
Write $f(\boldsymbol{w}\mid \boldsymbol{x})$ for the exposure density, and define the exponential tilt
\begin{align*}
g_{\boldsymbol{\delta}}(\boldsymbol{w}\mid \boldsymbol{x})
&:=\frac{\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})\}\,f(\boldsymbol{w}\mid \boldsymbol{x})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})},\\
\nu_{\boldsymbol{\delta}}(\boldsymbol{x})
&:=\mathbb E_f\big[\exp\{\boldsymbol{\delta}^\top\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\}\mid \boldsymbol{X}=\boldsymbol{x}\big].
\end{align*}
Let $\mu(\boldsymbol{x},\boldsymbol{w}):=\mathbb E[Y\mid \boldsymbol{X}=\boldsymbol{x},\boldsymbol{W}=\boldsymbol{w}]$, and denote
$$
\tilde{\boldsymbol{s}}(\boldsymbol{w},\boldsymbol{x})
:=\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\mathbb E_f[\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}=\boldsymbol{x}].
$$
All bounds are derived for a general tilt and then specialized to $\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})=\boldsymbol{w}$.

Assumptions:
\begin{description}
\item[(A1) Bounded outcomes] There exists $M<\infty$ such that $|Y|\le M$ a.s. Hence $|\mu(\boldsymbol{x},\boldsymbol{w})|\le M$.
\item[(A2) Nondegenerate noise] $0<\underline{\sigma}^2\le \Var(Y\mid \boldsymbol{X},\boldsymbol{W})\le \overline{\sigma}^2<\infty$ a.s.
\item[(A3) Bounded tilt] $\|\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})\|\le M_s<\infty$ and we require for some finite radius $\Delta\in(0,\infty)$ that $\|\boldsymbol{\delta}\|\le \Delta$. For the purpose of this proof, we assume there exists a fixed constant $C_{\delta}>0$ such that
$$
\|\boldsymbol{\delta}\|\ \le\ \frac{C_{\delta}}{M_s}\,.
$$
\item[(A4) Model richness] The class of distributions $\mathcal{P}$ is sufficiently rich. There exist constants $B, \epsilon_0 > 0$ such that for any $P_0 \in \mathcal{P}$, if $\phi \in L_\infty(P_0)$ with $\E_{P_0}[\phi(\boldsymbol{Z})]=0$ and $\|\phi\|_\infty \le B$, then for all $|\epsilon| \le \epsilon_0$, the density $p_0(1+\epsilon\phi)$ corresponds to a distribution $P_1 \in \mathcal{P}$.
\item[(A5) Pathwise differentiability] The functional $\psi(\cdot)$ is pathwise differentiable at any $P_0 \in \mathcal{P}$. The remainder from the von Mises expansion admits a uniform quadratic bound: there exists a constant $K < \infty$ such that for any perturbation $\phi$ with $\|\phi\|_\infty \le B$, the bound
$$
|\psi(P_0(1+\epsilon\phi)) - \psi(P_0) - \epsilon\E_{P_0}[\varphi(\boldsymbol{Z};P_0)\phi(\boldsymbol{Z})]| \le K\epsilon^2
$$
holds uniformly for all $P_0 \in \mathcal{P}$ and all valid $\phi$.
\end{description}

Identification and target.
Under standard consistency and conditional exchangeability,
\begin{align*}
\psi_P(\boldsymbol{\delta})
&=\mathbb E_P\Big[\int \mu(\boldsymbol{X},\boldsymbol{w})g_{\boldsymbol{\delta}}(\boldsymbol{w}\mid \boldsymbol{X})\,d\boldsymbol{w}\Big],\\
\theta_P(\boldsymbol{\delta})
&:=\psi_P(\boldsymbol{\delta})-\psi_P(\boldsymbol{0}).
\end{align*}

\subsection{Uniform second-order bounds}

This subsection derives uniform second-order $L_2(P_0)$ bounds for (i) the density ratio $g_{\boldsymbol{\delta}}/f$ and (ii) the tilted conditional mean $\mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]$, valid over a finite-tilt regime. The bounds provide an explicit quadratic remainder for the expansion around $\boldsymbol{\delta}=\boldsymbol{0}$ and uniform control of second-order terms in the Le Cam two-point construction underlying the minimax lower bound.

\begin{lemma}[Uniform $L_2$ bounds with explicit constants]
\label{lem:taylor-explicit}
Suppose (A1)–(A3). Let $\tau:=\|\boldsymbol{\delta}\|M_s\le C_{\delta}$. Then for all such $\boldsymbol{\delta}$,
\begin{align*}
\Big\|\frac{g_{\boldsymbol{\delta}}}{f}-1-\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}\Big\|_{L_2(P_0)}
&\le C_g\,\|\boldsymbol{\delta}\|^2,\\
\big\|\mathbb E_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]-\mathbb E_f[\mu\mid \boldsymbol{X}]-\boldsymbol{\delta}^\top \mathbb E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big\|_{L_2(P_0)}
&\le C_\mu\,\|\boldsymbol{\delta}\|^2,
\end{align*}
where one can take
\begin{align*}
C_g&:=4\,e^{2C_{\max}}\,M_s^2,\\
C_\mu&:=4\,e^{2C_{\max}}\,M\,M_s^2.
\end{align*}
\end{lemma}

\begin{proof}
All vector norms are Euclidean, and all matrix norms are operator norms. Expectations and conditional expectations are under the baseline law $P_0$ unless explicitly indicated. Write $M_s:=\sup_{\boldsymbol{w},\boldsymbol{x}}\|\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})\|<\infty$ by (A3), and $M:=\sup_{\boldsymbol{x},\boldsymbol{w}}|\mu(\boldsymbol{x},\boldsymbol{w})|<\infty$ by (A1). Let $\boldsymbol{\delta}\in\mathbb{R}^q$ and define
$$
\tau:=\|\boldsymbol{\delta}\|\,M_s.
$$
Under (A3),
$$
\|\boldsymbol{\delta}\|\ \le\ \frac{C_{\delta}}{M_s}
\quad\Longrightarrow\quad
\tau\le C_{\delta},
$$
which yields uniform bounds with explicit constants.

Define
\begin{align*}
r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})
&:=\frac{g_{\boldsymbol{\delta}}(\boldsymbol{w}\mid \boldsymbol{x})}{f(\boldsymbol{w}\mid \boldsymbol{x})}
=\frac{\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})\}}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})},\\
\nu_{\boldsymbol{\delta}}(\boldsymbol{x})
&:=\mathbb{E}_f\big[\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\}\,\big|\,\boldsymbol{X}=\boldsymbol{x}\big].
\end{align*}
Since $|\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})|\le \|\boldsymbol{\delta}\|\,\|\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})\|\le \tau\le C_{\delta}$, we have
\begin{align*}
e^{-\tau}\ \le\ \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})\}\ \le\ e^{\tau},\qquad
e^{-\tau}\ \le\ \nu_{\boldsymbol{\delta}}(\boldsymbol{x})\ \le\ e^{\tau}.
\end{align*}
It follows that
$$
0<e^{-2\tau}\ \le\ r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})\ \le\ e^{2\tau}\ \le\ e^{2C_{\max}}.
$$

\medskip\noindent
Second-order expansion of $r_{\boldsymbol{\delta}}$ and a uniform Hessian bound.
Introduce the log-partition function
$$
\log \nu_{\boldsymbol{\delta}}(\boldsymbol{x})
=\log \mathbb{E}_f\!\big[\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\}\,\big|\,\boldsymbol{X}=\boldsymbol{x}\big].
$$
Then
$$
r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})
=\exp\big\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\log \nu_{\boldsymbol{\delta}}(\boldsymbol{x})\big\}.
$$
Differentiating with respect to $\boldsymbol{\delta}$ yields
\begin{align*}
\nabla_{\boldsymbol{\delta}} \log \nu_{\boldsymbol{\delta}}(\boldsymbol{x})
&=\mathbb{E}_{g_{\boldsymbol{\delta}}}\!\big[\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\,\big|\,\boldsymbol{X}=\boldsymbol{x}\big]
=:\boldsymbol{\mu}_{g,s}(\boldsymbol{\delta},\boldsymbol{x}),\\
\nabla_{\boldsymbol{\delta}}^2 \log \nu_{\boldsymbol{\delta}}(\boldsymbol{x})
&=\Var_{g_{\boldsymbol{\delta}}}\!\big(\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\,\big|\,\boldsymbol{X}=\boldsymbol{x}\big),
\end{align*}
and therefore
\begin{align*}
\nabla_{\boldsymbol{\delta}} \log r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})
&=\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\boldsymbol{\mu}_{g,s}(\boldsymbol{\delta},\boldsymbol{x}),\\
\nabla_{\boldsymbol{\delta}}^2 \log r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})
&=-\,\Var_{g_{\boldsymbol{\delta}}}\!\big(\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\,\big|\,\boldsymbol{X}=\boldsymbol{x}\big).
\end{align*}
Using $\nabla F=F\,\nabla \log F$ and $\nabla^2 F=F\big[(\nabla\log F)(\nabla\log F)^\top+\nabla^2\log F\big]$, we obtain
\begin{align*}
\nabla_{\boldsymbol{\delta}} r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})
&=r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})\,\big[\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\boldsymbol{\mu}_{g,s}(\boldsymbol{\delta},\boldsymbol{x})\big],\\
\nabla_{\boldsymbol{\delta}}^2 r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})
&=r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})\,\Big(
\big[\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\boldsymbol{\mu}_{g,s}(\boldsymbol{\delta},\boldsymbol{x})\big]
\big[\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\boldsymbol{\mu}_{g,s}(\boldsymbol{\delta},\boldsymbol{x})\big]^\top\\
&\qquad\qquad\qquad\qquad
-\Var_{g_{\boldsymbol{\delta}}}\!\big(\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\,\big|\,\boldsymbol{X}=\boldsymbol{x}\big)
\Big).
\end{align*}
A uniform bound for the Hessian holds on the ball $\{\boldsymbol{\delta}:\ \|\boldsymbol{\delta}\|\le C_{\delta}/M_s\}$. First,
\begin{align*}
\|\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\boldsymbol{\mu}_{g,s}(\boldsymbol{\delta},\boldsymbol{x})\|
&\le \|\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})\|+\|\boldsymbol{\mu}_{g,s}(\boldsymbol{\delta},\boldsymbol{x})\|\\
&\le M_s+\mathbb{E}_{g_{\boldsymbol{\delta}}}[\|\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\|\mid \boldsymbol{X}=\boldsymbol{x}]
\le 2M_s,
\end{align*}
so
$$
\big\|\big[\boldsymbol{s}-\boldsymbol{\mu}_{g,s}\big]\big[\boldsymbol{s}-\boldsymbol{\mu}_{g,s}\big]^\top\big\|
\le \|\boldsymbol{s}-\boldsymbol{\mu}_{g,s}\|^2
\le 4M_s^2.
$$
Next, since $\|\boldsymbol{s}-\boldsymbol{\mu}_{g,s}\|\le 2M_s$,
\begin{align*}
\big\|\Var_{g_{\boldsymbol{\delta}}}(\boldsymbol{s}\mid \boldsymbol{X}=\boldsymbol{x})\big\|
&=\big\| \mathbb{E}_{g_{\boldsymbol{\delta}}}\big[(\boldsymbol{s}-\boldsymbol{\mu}_{g,s})(\boldsymbol{s}-\boldsymbol{\mu}_{g,s})^\top\mid \boldsymbol{X}=\boldsymbol{x}\big]\big\|\\
&\le \mathbb{E}_{g_{\boldsymbol{\delta}}}\big[\|\boldsymbol{s}-\boldsymbol{\mu}_{g,s}\|^2\mid \boldsymbol{X}=\boldsymbol{x}\big]
\le 4M_s^2.
\end{align*}
Combining these bounds with $0<r_{\boldsymbol{\delta}}\le e^{2\tau}\le e^{2C_{\max}}$ yields the uniform Hessian bound
\begin{equation}
\label{eq:Hessian-bound}
\big\|\nabla_{\boldsymbol{\delta}}^2 r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})\big\|
\le r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})\,\big(4M_s^2+4M_s^2\big)
\le 8\,e^{2C_{\max}}\,M_s^2,
\qquad \text{for all }(\boldsymbol{w},\boldsymbol{x})\text{ and all }\|\boldsymbol{\delta}\|\le \tfrac{C_{\delta}}{M_s}.
\end{equation}

\medskip\noindent
Proof of (i).
By Taylor's theorem with integral remainder for the scalar function $r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})$ around $\boldsymbol{\delta}=\boldsymbol{0}$,
\begin{align*}
r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})
&=r_{\boldsymbol{0}}(\boldsymbol{w},\boldsymbol{x})
+\nabla_{\boldsymbol{\delta}} r_{\boldsymbol{0}}(\boldsymbol{w},\boldsymbol{x})^\top \boldsymbol{\delta}\\
&\qquad
+\boldsymbol{\delta}^\top\!\Big(\int_0^1 (1-t)\,\nabla_{\boldsymbol{\delta}}^2 r_{t\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})\,dt\Big)\boldsymbol{\delta}.
\end{align*}
Since $\nu_{\boldsymbol{0}}(\boldsymbol{x})=1$,
\begin{align*}
r_{\boldsymbol{0}}(\boldsymbol{w},\boldsymbol{x})
&=1,\\
\nabla_{\boldsymbol{\delta}} r_{\boldsymbol{0}}(\boldsymbol{w},\boldsymbol{x})
&=\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\mathbb{E}_f[\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}=\boldsymbol{x}]
=\tilde{\boldsymbol{s}}(\boldsymbol{w},\boldsymbol{x}).
\end{align*}
Therefore,
\begin{align*}
r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})-1-\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}(\boldsymbol{w},\boldsymbol{x})
&=\boldsymbol{\delta}^\top\!\Big(\int_0^1 (1-t)\,\nabla_{\boldsymbol{\delta}}^2 r_{t\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})\,dt\Big)\boldsymbol{\delta}.
\end{align*}
By Taylor's theorem with integral remainder and \eqref{eq:Hessian-bound},
\begin{align*}
\big|r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})-1-\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}(\boldsymbol{w},\boldsymbol{x})\big|
&\le \Big(\int_0^1 (1-t)\,dt\Big)\,
\Big(\sup_{\boldsymbol{\xi}:\ \|\boldsymbol{\xi}\|\le \|\boldsymbol{\delta}\|}\big\|\nabla_{\boldsymbol{\delta}}^2 r_{\boldsymbol{\xi}}(\boldsymbol{w},\boldsymbol{x})\big\|\Big)\,\|\boldsymbol{\delta}\|^2\\
&\le 4\,e^{2C_{\max}}\,M_s^2\,\|\boldsymbol{\delta}\|^2.
\end{align*}
Hence,
$$
\Big\|r_{\boldsymbol{\delta}}-1-\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}\Big\|_{L_2(P_0)}\ \le\ 4\,e^{2C_{\max}}\,M_s^2\,\|\boldsymbol{\delta}\|^2,
$$
which proves part (i) with $C_g:=4e^{2C_{\max}}M_s^2$.

\medskip\noindent
Proof of (ii).
By definition of the tilt,
$$
\mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]
=\mathbb{E}_f\!\big[\mu(\boldsymbol{X},\boldsymbol{W})\,r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}\big].
$$
Therefore,
\begin{align*}
\mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]-\mathbb{E}_f[\mu\mid \boldsymbol{X}]
&=\mathbb{E}_f\!\big[\mu(\boldsymbol{X},\boldsymbol{W})\,\{r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})-1\}\mid \boldsymbol{X}\big]\\
&=\boldsymbol{\delta}^\top\,\mathbb{E}_f\big[\mu(\boldsymbol{X},\boldsymbol{W})\,\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}\big]
+\mathbb{E}_f\!\big[\mu(\boldsymbol{X},\boldsymbol{W})\,r_2(\boldsymbol{W},\boldsymbol{X};\boldsymbol{\delta})\mid \boldsymbol{X}\big],
\end{align*}
where
$$
r_2(\boldsymbol{w},\boldsymbol{x};\boldsymbol{\delta})
:=r_{\boldsymbol{\delta}}(\boldsymbol{w},\boldsymbol{x})-1-\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}(\boldsymbol{w},\boldsymbol{x}).
$$
Define
$$
R_\mu(\boldsymbol{X};\boldsymbol{\delta})
:=\mathbb{E}_f\!\big[\mu(\boldsymbol{X},\boldsymbol{W})\,r_2(\boldsymbol{W},\boldsymbol{X};\boldsymbol{\delta})\mid \boldsymbol{X}\big].
$$
By Cauchy--Schwarz and $|\mu|\le M$,
\begin{align*}
\|R_\mu(\cdot;\boldsymbol{\delta})\|_{L_2(P_0)}^2
&=\mathbb{E}\Big[\,\big(\mathbb{E}_f\big[\mu\,r_2\mid \boldsymbol{X}\big]\big)^2\,\Big]
\le \mathbb{E}\Big[\,\mathbb{E}_f\big[\mu^2\,r_2^2\mid \boldsymbol{X}\big]\,\Big]\\
&= \mathbb{E}\big[\mu^2 r_2^2\big]
\le M^2\,\|r_2\|_{L_2(P_0)}^2.
\end{align*}
From part (i), $\|r_2\|_{L_2(P_0)}\le C_g\,\|\boldsymbol{\delta}\|^2$ with $C_g=4\,e^{2C_{\max}}\,M_s^2$. Hence
$$
\|R_\mu(\cdot;\boldsymbol{\delta})\|_{L_2(P_0)}
\le M\,C_g\,\|\boldsymbol{\delta}\|^2
=4\,e^{2C_{\max}}\,M\,M_s^2\,\|\boldsymbol{\delta}\|^2.
$$
Thus
$$
\Big\|\mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]-\mathbb{E}_f[\mu\mid \boldsymbol{X}]-\boldsymbol{\delta}^\top \mathbb{E}_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\Big\|_{L_2(P_0)}
\le 4\,e^{2C_{\max}}\,M\,M_s^2\,\|\boldsymbol{\delta}\|^2,
$$
which proves part (ii) with $C_\mu:=4e^{2C_{\max}}MM_s^2$.
\end{proof}

\subsection{First-order expansion of the EIF and its covariance}

The second-order expansions above imply a first-order expansion of the efficient influence function for $\psi(\boldsymbol{\delta})$ at $\boldsymbol{\delta}=\boldsymbol{0}$, with leading term $\boldsymbol{\delta}^\top\boldsymbol{h}(\boldsymbol{Z})$ and a quadratic remainder.

\begin{lemma}[EIF expansion from the three-component decomposition]\label{lem:eif-grad-cov}
Let
$$
\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})=D_Y(\boldsymbol{Z})+D_{g,\mu}(\boldsymbol{Z})+D_{\psi}(\boldsymbol{Z}).
$$
Recall $\tilde{\boldsymbol{s}}(\boldsymbol{w},\boldsymbol{x}):=\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})-\E_f[\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}=\boldsymbol{x}]$, and define
$$
\boldsymbol{h}(\boldsymbol{Z})
:=\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\Big(Y-\E_f[\mu\mid \boldsymbol{X}]\Big)\;-\;\E\big[\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big].
$$
Assume (A1)–(A3) and $\|\boldsymbol{\delta}\|\le C_{\delta}/M_s$. Then, with the constants from Lemma~\ref{lem:taylor-explicit},
\begin{align*}
C_g&=4e^{2C_{\max}}M_s^2,\\
C_\mu&=4e^{2C_{\max}}MM_s^2,
\end{align*}
we have the expansion
$$
\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})
=\underbrace{Y-\psi_P(\boldsymbol{0})}_{\varphi_{\psi(\boldsymbol{0})}(\boldsymbol{Z})}
+\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})
+R_\varphi(\boldsymbol{Z};\boldsymbol{\delta}),
$$
and an explicit quadratic $L_2$ bound
\begin{align*}
\|R_\varphi(\cdot;\boldsymbol{\delta})\|_{L_2(P_0)}
&\le C_\varphi\,\|\boldsymbol{\delta}\|^2,\\
C_\varphi
&:=4M_s^2\Big(e^{2C_{\max}}\overline{\sigma}
+M\big(e^{4C_{\max}}+(4+2C_{\max})e^{2C_{\max}}+1\big)\Big).
\end{align*}
Consequently,
$$
\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})
:=\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})-\varphi_{\psi(\boldsymbol{0})}(\boldsymbol{Z})
=\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})+R_\varphi(\boldsymbol{Z};\boldsymbol{\delta}).
$$
We have $\mathbb{E}[\boldsymbol{h}(\boldsymbol{Z})]=\boldsymbol{0}$.
Moreover, the leading covariance of the influence function satisfies
\begin{align*}
\Cov\big(\boldsymbol{h}(\boldsymbol{Z})\big)
&=\E\!\Big[\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})^\top\Var(Y\mid \boldsymbol{X},\boldsymbol{W})\Big]\\
&\quad+\Cov\!\Big(\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\big(\mu(\boldsymbol{X},\boldsymbol{W})-\E_f[\mu\mid \boldsymbol{X}]\big)\Big)
=: \boldsymbol{\Sigma}_{\varepsilon, s}+\boldsymbol{\Sigma}_{\mu,\mathrm{full}},
\end{align*}
where
\begin{align*}
\boldsymbol{\Sigma}_{\varepsilon, s}
&:=\E\big[\Var(Y\mid \boldsymbol{X},\boldsymbol{W})\,\tilde{\boldsymbol{s}}\tilde{\boldsymbol{s}}^\top\big],\\
\boldsymbol{C}
&:=\E\!\big[\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big],\\
\boldsymbol{\Sigma}_{\mu,\mathrm{full}}
&:=\E\!\Big[\tilde{\boldsymbol{s}}\tilde{\boldsymbol{s}}^\top\big(\mu-\E_f[\mu\mid \boldsymbol{X}]\big)^2\Big]-\boldsymbol{C}\boldsymbol{C}^\top.
\end{align*}
In particular,
$$
\boldsymbol{\Sigma}_{\mu,\mathrm{full}}\succeq \underbrace{\Cov\!\big(\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big)}_{=:\ \boldsymbol{\Sigma}_\mu}.
$$
Equality $\boldsymbol{\Sigma}_{\mu,\mathrm{full}}=\boldsymbol{\Sigma}_\mu$ holds if and only if $\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\{\mu(\boldsymbol{X},\boldsymbol{W})-\E_f[\mu\mid \boldsymbol{X}]\}$ is conditionally degenerate given $\boldsymbol{X}$.
\end{lemma}

\begin{proof}
\medskip\noindent
\textit{Preliminaries.}
Recall
$$
r_{\boldsymbol{\delta}}(\boldsymbol{W},\boldsymbol{X})
:=\frac{g_{\boldsymbol{\delta}}(\boldsymbol{W}\mid \boldsymbol{X})}{f(\boldsymbol{W}\mid \boldsymbol{X})}.
$$
By Lemma~\ref{lem:taylor-explicit}, for $\|\boldsymbol{\delta}\|\le C_{\delta}/M_s$ there exist remainders $r_2(\boldsymbol{W},\boldsymbol{X};\boldsymbol{\delta})$ and $r_\mu(\boldsymbol{X};\boldsymbol{\delta})$ such that
\begin{align*}
r_{\boldsymbol{\delta}}&=1+\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}+r_2,
\qquad \|r_2\|_{L_2(P_0)}\le C_g\|\boldsymbol{\delta}\|^2,\\
\E_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]
&=\E_f[\mu\mid \boldsymbol{X}]+\boldsymbol{\delta}^\top \E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]+r_\mu,
\qquad \|r_\mu\|_{L_2(P_0)}\le C_\mu\|\boldsymbol{\delta}\|^2.
\end{align*}
The tilt radius implies $0<r_{\boldsymbol{\delta}}\le e^{2\tau}\le e^{2C_{\max}}$ with $\tau=\|\boldsymbol{\delta}\|M_s\le C_{\delta}$, hence $\|r_{\boldsymbol{\delta}}\|_\infty\le e^{2C_{\max}}$. We also use $\|\tilde{\boldsymbol{s}}\|_\infty\le 2M_s$, $|\mu|\le M$, and $\|\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\|_\infty\le 2MM_s$.

Also,
\begin{align*}
\psi_P(\boldsymbol{\delta})
&=\mathbb{E}\!\left[\mathbb{E}_{g_{\boldsymbol{\delta}}}[\mu \mid \boldsymbol{X}]\right]\\
&=\psi_P(\boldsymbol{0})
+\boldsymbol{\delta}^{\top}\, \mathbb{E}\!\left[\mathbb{E}_f[\mu \tilde{\boldsymbol{s}} \mid \boldsymbol{X}]\right]
+\mathbb{E}\!\left[r_\mu(\boldsymbol{X};\boldsymbol{\delta})\right].
\end{align*}

\medskip\noindent
\textit{Expansion of EIF components.}
Using the displays above,
\begin{align*}
D_Y
&=r_{\boldsymbol{\delta}}\,(Y-\mu)
=(1+\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}+r_2)(Y-\mu)\\
&=(Y-\mu)+\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}\,(Y-\mu)+r_2\,(Y-\mu),
\end{align*}
\begin{align*}
D_{g,\mu}
&=r_{\boldsymbol{\delta}}\big(\mu-\E_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]\big)\\
&=(1+\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}+r_2)\Big(\mu-\E_f[\mu\mid \boldsymbol{X}]-\boldsymbol{\delta}^\top\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]-r_\mu\Big)\\
&=(\mu-\E_f[\mu\mid \boldsymbol{X}])
+\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}\,(\mu-\E_f[\mu\mid \boldsymbol{X}])
-\boldsymbol{\delta}^\top\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]
+R_2,
\end{align*}
\begin{align*}
D_{\psi}
&=\E_{g_{\boldsymbol{\delta}}}[\mu\mid \boldsymbol{X}]-\psi_P(\boldsymbol{\delta})\\
&=\E_f[\mu\mid \boldsymbol{X}]-\psi_P(\boldsymbol{0})
+\boldsymbol{\delta}^\top\Big(\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]-\E[\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]]\Big)
+(r_\mu-\E[r_\mu]),
\end{align*}
where the remainder $R_2$ collects all quadratic and higher-order terms:
\begin{align*}
R_2
&:=r_2(\mu-\E_f[\mu\mid \boldsymbol{X}])
-(1+\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}+r_2)\,r_\mu\\
&\quad-(\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}})\big(\boldsymbol{\delta}^\top \E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big)
-r_2\,\big(\boldsymbol{\delta}^\top \E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big).
\end{align*}

\medskip\noindent
\textit{Collection of zero and first-order terms.}
Adding $D_Y+D_{g,\mu}+D_{\psi}$ gives
\begin{align*}
\varphi_{\psi(\boldsymbol{\delta})}
&=\Big[Y-\psi_P(\boldsymbol{0})\Big]\\
&\quad+\boldsymbol{\delta}^\top\Big[\tilde{\boldsymbol{s}}\big(Y-\E_f[\mu\mid \boldsymbol{X}]\big)-\E\big[\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big]\Big]\\
&\quad+\underbrace{\Big\{r_2(Y-\mu)+R_2+(r_\mu-\E[r_\mu])\Big\}}_{=:R_\varphi}.
\end{align*}
Hence the first-order term is $\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})$.

\medskip\noindent
\textit{Explicit $L_2$ bounds for remainder terms.}
By Cauchy--Schwarz and (A2),
$$
\|r_2(Y-\mu)\|_{L_2}\ \le\ \overline{\sigma}\,\|r_2\|_{L_2}\ \le\ C_g\,\overline{\sigma}\,\|\boldsymbol{\delta}\|^2.
$$
Since $\|\mu-\E_f[\mu\mid \boldsymbol{X}]\|_\infty\le 2M$,
$$
\|r_2(\mu-\E_f[\mu\mid \boldsymbol{X}])\|_{L_2}\ \le\ 2M\,\|r_2\|_{L_2}\ \le\ 2M\,C_g\,\|\boldsymbol{\delta}\|^2.
$$
Using $\|r_{\boldsymbol{\delta}}\|_\infty\le e^{2C_{\max}}$,
$$
\|(1+\boldsymbol{\delta}^\top\tilde{\boldsymbol{s}}+r_2)\,r_\mu\|_{L_2}
=\|r_{\boldsymbol{\delta}} r_\mu\|_{L_2}
\le e^{2C_{\max}}\,C_\mu\,\|\boldsymbol{\delta}\|^2.
$$
Moreover,
$$
\|r_\mu-\E[r_\mu]\|_{L_2}\ \le\ \|r_\mu\|_{L_2}+\|\E[r_\mu]\|_{L_2}\ \le\ 2C_\mu\,\|\boldsymbol{\delta}\|^2.
$$
For the quadratic product,
\begin{align*}
\big\|(\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}})\big(\boldsymbol{\delta}^\top \E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big)\big\|_{L_2}
&\le \|\boldsymbol{\delta}^\top \E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\|_\infty\,\|\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}\|_{L_2}\\
&\le (2MM_s\|\boldsymbol{\delta}\|)\,(2M_s\|\boldsymbol{\delta}\|)
=4MM_s^2\,\|\boldsymbol{\delta}\|^2.
\end{align*}
Finally,
\begin{align*}
\big\|r_2\,(\boldsymbol{\delta}^\top \E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}])\big\|_{L_2}
&\le \|r_2\|_{L_2}\,\|\boldsymbol{\delta}^\top \E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\|_\infty\\
&\le C_g\|\boldsymbol{\delta}\|^2\cdot (2MM_s\|\boldsymbol{\delta}\|)\\
&\le 2C_{\max}\,M\,C_g\,\|\boldsymbol{\delta}\|^2,
\end{align*}
where we used $\|\boldsymbol{\delta}\|\le C_{\delta}/M_s$. Combining all displays yields
\begin{align*}
\|R_\varphi\|_{L_2}
&\le C_g\,\overline{\sigma}\,\|\boldsymbol{\delta}\|^2
+2M\,C_g\,\|\boldsymbol{\delta}\|^2
+e^{2C_{\max}}\,C_\mu\,\|\boldsymbol{\delta}\|^2
+2C_\mu\,\|\boldsymbol{\delta}\|^2\\
&\quad+4MM_s^2\,\|\boldsymbol{\delta}\|^2
+2C_{\max}\,M\,C_g\,\|\boldsymbol{\delta}\|^2
\le C_\varphi\,\|\boldsymbol{\delta}\|^2,
\end{align*}
with $C_\varphi$ as stated.

\medskip\noindent
\textit{Covariance of the gradient.}
Write
\begin{align*}
m(\boldsymbol{X})&=\E_f[\mu\mid \boldsymbol{X}],\\
\boldsymbol{C}&=\E\!\big[\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big],\\
\boldsymbol{h}(\boldsymbol{Z})&=\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\big(Y-m(\boldsymbol{X})\big)-\boldsymbol{C}.
\end{align*}
Set
\begin{align*}
\boldsymbol{U}&:=\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\big(Y-\mu(\boldsymbol{X},\boldsymbol{W})\big),\\
\boldsymbol{V}&:=\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\big(\mu(\boldsymbol{X},\boldsymbol{W})-m(\boldsymbol{X})\big),
\end{align*}
so that $\boldsymbol{h}=\boldsymbol{U}+(\boldsymbol{V}-\boldsymbol{C})$.
Because $\mathbb{E}[\boldsymbol{U} \mid \boldsymbol{X}, \boldsymbol{W}] = \boldsymbol{0}$ and $\boldsymbol{V} - \boldsymbol{C}$ is measurable with respect to $(\boldsymbol{X}, \boldsymbol{W})$, 
$\mathrm{Cov}(\boldsymbol{U}, \boldsymbol{V} - \boldsymbol{C}) = \boldsymbol{0}$, hence
$$
\Cov(\boldsymbol{h})
=\Cov(\boldsymbol{U})+\Cov(\boldsymbol{V}-\boldsymbol{C}).
$$
Moreover, conditioning on $(\boldsymbol{X},\boldsymbol{W})$ gives
$$
\Cov(\boldsymbol{U})
=\E\!\Big[\tilde{\boldsymbol{s}}\tilde{\boldsymbol{s}}^\top\Var(Y\mid \boldsymbol{X},\boldsymbol{W})\Big]
=:\boldsymbol{\Sigma}_{\varepsilon, s},
$$
and
\begin{align*}
\Cov(\boldsymbol{V}-\boldsymbol{C})
&=\Cov(\boldsymbol{V})
=\E[\boldsymbol{V}\boldsymbol{V}^\top]-\boldsymbol{C}\boldsymbol{C}^\top\\
&=\E\!\Big[\tilde{\boldsymbol{s}}\tilde{\boldsymbol{s}}^\top\big(\mu-\E_f[\mu\mid \boldsymbol{X}]\big)^2\Big]-\boldsymbol{C}\boldsymbol{C}^\top
=:\boldsymbol{\Sigma}_{\mu,\mathrm{full}}.
\end{align*}
Thus $\Cov(\boldsymbol{h})=\boldsymbol{\Sigma}_{\varepsilon, s}+\boldsymbol{\Sigma}_{\mu,\mathrm{full}}$.

Finally, the law of total covariance yields
\begin{align*}
\boldsymbol{\Sigma}_{\mu,\mathrm{full}}
&=\E\big[\Var(\boldsymbol{V}\mid \boldsymbol{X})\big]+\Cov\big(\E[\boldsymbol{V}\mid \boldsymbol{X}]\big)
\succeq \Cov\big(\E[\boldsymbol{V}\mid \boldsymbol{X}]\big)\\
&=\Cov\!\big(\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\big)
=:\boldsymbol{\Sigma}_\mu.
\end{align*}

\medskip\noindent
\textit{Mean zero property of $\boldsymbol{h}$.}
Let $m(\boldsymbol{X})=\E_f[\mu\mid \boldsymbol{X}]$ and $\boldsymbol{C}=\E[\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]]$.
Using the definition of $\boldsymbol{h}$,
\begin{align*}
\boldsymbol{h}(\boldsymbol{Z})
&=\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\,\big(Y-m(\boldsymbol{X})\big)-\boldsymbol{C}\\
&=\underbrace{\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\,\big(Y-\mu(\boldsymbol{X},\boldsymbol{W})\big)}_{=:\boldsymbol{U}}
+\underbrace{\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\,\big(\mu(\boldsymbol{X},\boldsymbol{W})-m(\boldsymbol{X})\big)}_{=:\boldsymbol{V}}
-\boldsymbol{C}.
\end{align*}
The expectation decomposes as $\mathbb{E}[\boldsymbol{h}]=\mathbb{E}[\boldsymbol{U}]+\mathbb{E}[\boldsymbol{V}]-\boldsymbol{C}$.

First,
\begin{align*}
\mathbb{E}[\boldsymbol{U}]
&=\mathbb{E}\!\left[\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\,\mathbb{E}\big[Y-\mu(\boldsymbol{X},\boldsymbol{W})\mid \boldsymbol{X},\boldsymbol{W}\big]\right]\\
&=\mathbb{E}\!\left[\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\cdot 0\right]=\boldsymbol{0}.
\end{align*}

Second, for $\boldsymbol{V}$,
\begin{align*}
\mathbb{E}[\boldsymbol{V}]
&=\mathbb{E}\!\left[\mathbb{E}\big[\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\,\mu(\boldsymbol{X},\boldsymbol{W})\mid \boldsymbol{X}\big]\right]
-\mathbb{E}\!\left[m(\boldsymbol{X})\,\mathbb{E}\big[\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}\big]\right].
\end{align*}
By definition $\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})=\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})-\mathbb{E}_f[\boldsymbol{s}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}]$, hence
$$
\mathbb{E}\big[\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}\big]=\boldsymbol{0},
$$
so
$$
\mathbb{E}[\boldsymbol{V}]
=\mathbb{E}\!\left[\mathbb{E}_f[\mu\,\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]\right]
=\boldsymbol{C}.
$$
Putting the pieces together,
$$
\mathbb{E}[\boldsymbol{h}]
=\mathbb{E}[\boldsymbol{U}]+\mathbb{E}[\boldsymbol{V}]-\boldsymbol{C}
=\boldsymbol{0}+\boldsymbol{C}-\boldsymbol{C}
=\boldsymbol{0}.
$$
\end{proof}

\begin{corollary}\label{cor:var-squeeze-H}
Specializing Lemma~\ref{lem:eif-grad-cov} to $\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})=\boldsymbol{w}$ (so $\tilde{\boldsymbol{s}}=\tilde{\boldsymbol{W}}$), let
$$
\boldsymbol{H}
:=\Cov\!\big(\boldsymbol{h}(\boldsymbol{Z})\big)
=\boldsymbol{\Sigma}_{\varepsilon, s}+\boldsymbol{\Sigma}_{\mu,\mathrm{full}}
\succeq\boldsymbol{0}.
$$
Then, for all $\|\boldsymbol{\delta}\|\le C_{\delta}/M_s$,
\begin{align*}
\big(\sqrt{\boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}}-C_\varphi\|\boldsymbol{\delta}\|^2\big)_+^{\,2}
\ \le\ \Var\!\big\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\big\}
\ \le\ \big(\sqrt{\boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}}+C_\varphi\|\boldsymbol{\delta}\|^2\big)^{2},
\end{align*}
where $(x)_+=\max\{x,0\}$ and $C_\varphi$ is the constant in Lemma~\ref{lem:eif-grad-cov}.
Moreover, if $\lambda_{\min}(\boldsymbol{H})>0$ and $\|\boldsymbol{\delta}\|\le r_0$ for some
$$
r_0\ <\ \frac{\sqrt{\lambda_{\min}(\boldsymbol{H})}}{C_\varphi}\,,
$$
then there exist constants
\begin{align*}
c_{\mathrm{low}}
&:=\Big(1-\frac{C_\varphi\,r_0}{\sqrt{\lambda_{\min}(\boldsymbol{H})}}\Big)^2,\\
c_{\mathrm{up}}
&:=\Big(1+\frac{C_\varphi\,r_0}{\sqrt{\lambda_{\min}(\boldsymbol{H})}}\Big)^2,
\end{align*}
depending only on $(\boldsymbol{H},C_\varphi,r_0)$ but not on $\boldsymbol{\delta}$, such that
$$
c_{\mathrm{low}}\ \boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}
\ \le\ \Var\!\big\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\big\}
\ \le\ c_{\mathrm{up}}\ \boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}
\qquad \text{for all }\ \|\boldsymbol{\delta}\|\le r_0.
$$
Since
$$
\boldsymbol{H}=\boldsymbol{\Sigma}_{\varepsilon, s}+\boldsymbol{\Sigma}_{\mu,\mathrm{full}}\succeq \boldsymbol{\Sigma}_{\varepsilon, s},
$$
the lower bound immediately implies
$$
\Var\!\big\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\big\}\ \ge\ c_{\mathrm{low}}\ \boldsymbol{\delta}^\top \boldsymbol{\Sigma}_{\varepsilon, s}\,\boldsymbol{\delta}.
$$
\end{corollary}

\begin{proof}
By Lemma~\ref{lem:eif-grad-cov},
$$
\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})
=\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})+R_\varphi(\boldsymbol{Z};\boldsymbol{\delta}),
\qquad
\|R_\varphi(\cdot;\boldsymbol{\delta})\|_{L_2}\le C_\varphi\,\|\boldsymbol{\delta}\|^2,
\qquad
\E\{\boldsymbol{h}(\boldsymbol{Z})\}=\boldsymbol{0}.
$$
Write $A:=\boldsymbol{\delta}^\top \boldsymbol{h}$ and $R:=R_\varphi(\cdot;\boldsymbol{\delta})$, and center the remainder by $R_c:=R-\E[R]$.
Then
$$
\Var\!\big\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\big\}
=\Var(A+R)
=\Var(A+R_c)
=\|A+R_c\|_2^2.
$$
Because $\E[\boldsymbol{h}]=\boldsymbol{0}$, we have $\|A\|_2^2=\Var(A)=\boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}$.
Also $\|R_c\|_2=\sqrt{\Var(R)}\le \|R\|_2\le C_\varphi\|\boldsymbol{\delta}\|^2$ by Cauchy--Schwarz. 

By the triangle inequality and its reverse in $L_2$,
$$
\big|\ \|A\|_2-\|R_c\|_2\ \big|\ \le\ \|A+R_c\|_2\ \le\ \|A\|_2+\|R_c\|_2.
$$
Using $\|A\|_2=\sqrt{\boldsymbol{\delta}^\top \boldsymbol{H}\boldsymbol{\delta}}$ and $\|R_c\|_2\le C_\varphi\|\boldsymbol{\delta}\|^2$ and squaring both sides yields the additive bracket.

Suppose $\lambda_{\min}(\boldsymbol{H})>0$. Then, for all $\boldsymbol{\delta}$,
$$
\sqrt{\boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}}\ \ge\ \sqrt{\lambda_{\min}(\boldsymbol{H})}\,\|\boldsymbol{\delta}\|.
$$
Hence, for any $\|\boldsymbol{\delta}\|\le r_0$,
\begin{align*}
\frac{\|R_c\|_2}{\sqrt{\boldsymbol{\delta}^\top \boldsymbol{H}\,\boldsymbol{\delta}}}
&\le \frac{C_\varphi\|\boldsymbol{\delta}\|^2}{\sqrt{\lambda_{\min}(\boldsymbol{H})}\,\|\boldsymbol{\delta}\|}\\
&\le \frac{C_\varphi\,r_0}{\sqrt{\lambda_{\min}(\boldsymbol{H})}}
=:\ r_* \ <\ 1.
\end{align*}
Dividing the additive bracket by $\boldsymbol{\delta}^\top \boldsymbol{H}\boldsymbol{\delta}$ yields the multiplicative squeeze with
$$
c_{\mathrm{low}}=(1-r_*)^2,\qquad c_{\mathrm{up}}=(1+r_*)^2.
$$
Finally, because $\boldsymbol{H}\succeq \boldsymbol{\Sigma}_{\varepsilon, s}$, the coarser lower bound follows.
\end{proof}

\begin{lemma}[Hardest direction after orthogonalization]
\label{lem:orthopath-detailed}
Let $\varphi_0(\boldsymbol{Z}):=\varphi_{\psi(\boldsymbol{0})}(\boldsymbol{Z})=Y-\psi(\boldsymbol{0})$ and
\begin{align*}
\tilde\phi_0(\boldsymbol{Z})
&:=\frac{\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})}{\sqrt{\Var\!\big(\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})\big)}},\\
\sigma_h^2
&:=\Var\!\big(\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})\big).
\end{align*}
Define
\begin{align*}
\rho
&:=\text{Corr}(\tilde\phi_0,\varphi_0)
=\frac{\mathbb E[\tilde\phi_0\varphi_0]}{\sqrt{\Var(\varphi_0)}},\\
\phi(\boldsymbol{Z})
&:=\frac{\tilde{\phi}_0(\boldsymbol{Z})-\mathbb E[\tilde{\phi}_0\varphi_0]\cdot\frac{\varphi_0(\boldsymbol{Z})}{\Var(\varphi_0)}}{\sqrt{\,1-\frac{\big(\mathbb E[\tilde{\phi}_0\varphi_0]\big)^2}{\Var(\varphi_0)}\,}}.
\end{align*}
Then $\mathbb E[\phi]=0$, $\Var(\phi)=1$, and $\mathbb E[\phi\,\varphi_0]=0$.
Let Assumption (A4) hold with constants $(B,\varepsilon_0)$.
Consider $P_1$ with density $p_1=p_0(1+\varepsilon\phi)$, where $|\varepsilon|\le\min\{\varepsilon_0,\tfrac{1}{2B}\}$.
Then $p_1\in\mathcal P$, $\int p_1=1$, and $p_1\ge \tfrac12 p_0$. Moreover, for $\|\boldsymbol{\delta}\|\le C_{\delta}/M_s$,
\begin{align*}
\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})
&=\varepsilon\,\mathbb E\big[\phi\,\varphi_{\theta(\boldsymbol{\delta})}\big]+ r_\mathrm{A5}(\varepsilon)\\
&=\varepsilon\Big(\sqrt{\Var(\boldsymbol{\delta}^\top \boldsymbol{h})}\cdot\sqrt{1-\rho^2}\Big)
+\varepsilon\,\mathbb E[\phi\,R_\varphi(\cdot;\boldsymbol{\delta})]
+r_\mathrm{A5}(\varepsilon),
\end{align*}
where $R_\varphi(\cdot;\boldsymbol{\delta})$ is the remainder in the linear expansion $\varphi_{\theta(\boldsymbol{\delta})}=\boldsymbol{\delta}^\top \boldsymbol{h}+R_\varphi(\cdot;\boldsymbol{\delta})$, and the remainders satisfy
\begin{align*}
\big|\mathbb E[\phi\,R_\varphi(\cdot;\boldsymbol{\delta})]\big|
&\le \|R_\varphi(\cdot;\boldsymbol{\delta})\|_{L_2}
\le C_\varphi\,\|\boldsymbol{\delta}\|^2,\\
|r_\mathrm{A5}(\varepsilon)|
&\le 2K\,\varepsilon^2,
\end{align*}
with $C_\varphi$ as in Lemma~\ref{lem:eif-grad-cov} and $K$ the differentiability modulus from (A5). Finally,
$$
\chi^2(P_1,P_0)=\varepsilon^2
\qquad\text{and}\qquad
D_{\mathrm{KL}}(P_1\|P_0)\le \log(1+\varepsilon^2)\le \varepsilon^2.
$$
\end{lemma}

\begin{proof}
\medskip\noindent
\textit{Properties of $\phi$.}
Write $\sigma_0^2:=\Var(\varphi_0)$, so $\rho=\mathbb E[\tilde\phi_0\varphi_0]/\sigma_0$.
By construction,
$$
\phi=\frac{\tilde\phi_0 - (\mathbb E[\tilde\phi_0\varphi_0]/\sigma_0^2)\,\varphi_0}{\sqrt{\,1-\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2\,}}.
$$
Since $\mathbb E[\tilde\phi_0]=0$ and $\mathbb E[\varphi_0]=0$, we have $\mathbb E[\phi]=0$.
Next,
\begin{align*}
\Var(\phi)
&=\frac{\Var(\tilde\phi_0)+(\mathbb E[\tilde\phi_0\varphi_0]/\sigma_0^2)^2\Var(\varphi_0)-2(\mathbb E[\tilde\phi_0\varphi_0]/\sigma_0^2)\Cov(\tilde\phi_0,\varphi_0)}{1-\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2}\\
&=\frac{1+\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2-2\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2}{1-\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2}
=1.
\end{align*}
Also,
$$
\mathbb E[\phi\,\varphi_0]
=\frac{\mathbb E[\tilde\phi_0\varphi_0]-(\mathbb E[\tilde\phi_0\varphi_0]/\sigma_0^2)\,\sigma_0^2}{\sqrt{\,1-\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2\,}}=0.
$$
Finally,
\begin{align*}
\mathbb E[\phi\,\tilde\phi_0]
&=\frac{\mathbb E[\tilde\phi_0^2]- (\mathbb E[\tilde\phi_0\varphi_0]/\sigma_0^2)\mathbb E[\tilde\phi_0\varphi_0]}{\sqrt{\,1-\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2\,}}
=\sqrt{\,1-\mathbb E[\tilde\phi_0\varphi_0]^2/\sigma_0^2\,}
=\sqrt{1-\rho^2}.
\end{align*}
Because $\tilde\phi_0=\sigma_h^{-1}\boldsymbol{\delta}^\top \boldsymbol{h}$, we obtain
$$
\mathbb E\big[\phi\,\boldsymbol{\delta}^\top \boldsymbol{h}\big]
=\sigma_h\,\mathbb E[\phi\,\tilde\phi_0]
=\sigma_h\sqrt{1-\rho^2}.
$$

\medskip\noindent
\textit{Validity of $p_1$.}
By the definition of $\varepsilon_0$ in (A4), for every $\phi\in L_\infty$ with $\mathbb E[\phi]=0$ and $\|\phi\|_\infty\le B$, the measure with density $p_0(1+\varepsilon\phi)$ lies in $\mathcal P$ for all $|\varepsilon|\le\varepsilon_0$.
Moreover, $\int p_1=\int p_0(1+\varepsilon\phi)=1+\varepsilon\,\mathbb E[\phi]=1$.
If $|\varepsilon|\le (2B)^{-1}$ then $1+\varepsilon\phi\ge 1-|\varepsilon|\,\|\phi\|_\infty\ge 1/2$, so $p_1\ge \tfrac12 p_0$.

\medskip\noindent
\textit{First-order expansion of $\theta$ via (A5).}
By (A5), for $|\varepsilon|\le\varepsilon_0$,
\begin{align*}
\psi_{P_0(1+\varepsilon\phi)}(\boldsymbol{\delta})-\psi_{P_0}(\boldsymbol{\delta})
&=\varepsilon\,\mathbb E_{P_0}\!\big[\varphi_{\psi(\boldsymbol{\delta})}\,\phi\big]+ r_1(\varepsilon),
\qquad |r_1(\varepsilon)|\le K\varepsilon^2,\\
\psi_{P_0(1+\varepsilon\phi)}(\boldsymbol{0})-\psi_{P_0}(\boldsymbol{0})
&=\varepsilon\,\mathbb E_{P_0}\!\big[\varphi_{\psi(\boldsymbol{0})}\,\phi\big]+ r_0(\varepsilon),
\qquad |r_0(\varepsilon)|\le K\varepsilon^2.
\end{align*}
Subtracting gives
$$
\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})
=\varepsilon\,\mathbb E\big[\phi\,\varphi_{\theta(\boldsymbol{\delta})}\big] + r_\mathrm{A5}(\varepsilon),
\qquad
|r_\mathrm{A5}(\varepsilon)|\le 2K\varepsilon^2.
$$

\medskip\noindent
\textit{Evaluation of the leading inner product and remainder bound.}
By the linearization,
$$
\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})
=\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})+R_\varphi(\boldsymbol{Z};\boldsymbol{\delta}),
\qquad
\|R_\varphi(\cdot;\boldsymbol{\delta})\|_{L_2}\le C_\varphi\,\|\boldsymbol{\delta}\|^2,
$$
for all $\|\boldsymbol{\delta}\|\le C_{\delta}/M_s$. Hence
\begin{align*}
\mathbb E\big[\phi\,\varphi_{\theta(\boldsymbol{\delta})}\big]
&=\mathbb E[\phi\,\boldsymbol{\delta}^\top \boldsymbol{h}]+\mathbb E[\phi\,R_\varphi]\\
&=\sigma_h\sqrt{1-\rho^2}+\mathbb E[\phi\,R_\varphi],
\qquad
|\mathbb E[\phi\,R_\varphi]|\le C_\varphi\,\|\boldsymbol{\delta}\|^2.
\end{align*}
\end{proof}

\subsection{Minimax Lower Bound}

Recall
\begin{align*}
\boldsymbol{H}&:=\Cov\!\big(\boldsymbol{h}(\boldsymbol{Z})\big),\\
\sigma_0^2&:=\Var(\varphi_0)=\Var(Y-\psi(\boldsymbol{0})).
\end{align*}
Define the projected covariance (Schur complement) of the linear regression of $\boldsymbol{h}$ onto the one-dimensional span of $\varphi_0$:
\begin{align*}
\boldsymbol{\Gamma}
&:=\boldsymbol{H}
-\frac{\Cov\big(\boldsymbol{h},\varphi_0\big)\,\Cov\big(\boldsymbol{h},\varphi_0\big)^\top}{\sigma_0^2}
\succeq \boldsymbol{0}.
\end{align*}

\begin{theorem}[Minimax lower bound]
\label{thm:minimax-projected}
Assume (A1)–(A5). Fix some $\kappa\in(0,1)$ and assume
\begin{align*}
\|\boldsymbol{\delta}\|
\ \le\
\min\Big\{
\frac{C_{\delta}}{M_s},\ (1-\kappa)\frac{\sqrt{\lambda_{\min}(\boldsymbol{\Gamma})}}{C_\varphi}
\Big\}.
\end{align*}
If $\boldsymbol{\Gamma}$ is positive definite, then there exists a constant $C>0$ that depends only on $\kappa$ and the constants in (A1)–(A5), but not on $\boldsymbol{\delta}$, such that
$$
\liminf_{n\to\infty}\ \inf_{\hat\theta}\ \sup_{P\in\mathcal P}\ 
\frac{n\,\mathbb E_P\big[(\hat\theta-\theta_P(\boldsymbol{\delta}))^2\big]}{\boldsymbol{\delta}^\top \boldsymbol{\Gamma}\,\boldsymbol{\delta}}
\ \ge\ C.
$$
In particular, the lower bound is expressed in terms of $\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}$ and generally cannot be strengthened by replacing $\boldsymbol{\Gamma}$ with a larger matrix.
\end{theorem}

\begin{proof}[Proof of Theorem~\ref{thm:minimax-projected}]

\medskip\noindent
\textit{Notation.}

Let $\sigma_h^2:=\Var(\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z}))$, $\sigma_0^2:=\Var(\varphi_0(\boldsymbol{Z}))$, and $\tilde\phi_0:=\frac{\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})}{\sigma_h}$.

Define $\rho:=\text{Corr}(\tilde\phi_0,\varphi_0(\boldsymbol{Z}))=\frac{\Cov(\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z}),\varphi_0(\boldsymbol{Z}))}{\sigma_h\,\sigma_0}$.

\medskip\noindent
\textit{Two-point construction.}
Fix $P_0\in\mathcal P$ and let $\phi$ be as in Lemma~\ref{lem:orthopath-detailed}. For a given $n$, choose
\begin{align*}
\alpha_0&:=\min\Big\{\varepsilon_0,\ \frac{1}{2B},\ \frac{1}{2}\Big\},\\
\varepsilon&:=\frac{\alpha_0}{\sqrt{n}}.
\end{align*}
Then $|\varepsilon|\le \min\{\varepsilon_0,(2B)^{-1}\}$, and the perturbed model $P_1$ defined by $p_1=p_0(1+\varepsilon\phi)$ lies in $\mathcal P$, integrates to $1$, and satisfies $p_1\ge \tfrac12 p_0$.

\medskip\noindent
\textit{Parameter gap and the Schur complement.}
By Lemma~\ref{lem:orthopath-detailed},
\begin{align*}
\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})
&=\varepsilon\Big(\sigma_h\sqrt{1-\rho^2}\Big)
+\varepsilon\,\mathbb E[\phi\,R_\varphi(\cdot;\boldsymbol{\delta})]
+r_\mathrm{A5}(\varepsilon),
\end{align*}
with
$$
|\mathbb E[\phi\,R_\varphi(\cdot;\boldsymbol{\delta})]|\le C_\varphi\|\boldsymbol{\delta}\|^2,
\qquad
|r_\mathrm{A5}(\varepsilon)|\le 2K\varepsilon^2.
$$
Moreover,
\begin{align*}
\sigma_h\sqrt{1-\rho^2}
&=\sqrt{\Var(\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z}))-\frac{\Cov(\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z}),\varphi_0(\boldsymbol{Z}))^2}{\Var(\varphi_0(\boldsymbol{Z}))}}
=\sqrt{\boldsymbol{\delta}^\top \boldsymbol{\Gamma}\,\boldsymbol{\delta}}.
\end{align*}
Therefore
\begin{align*}
\Big|\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})\Big|
&\ge |\varepsilon|\Big(\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}-C_\varphi\|\boldsymbol{\delta}\|^2\Big)-2K\varepsilon^2.
\end{align*}
Using $\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}\ge \sqrt{\lambda_{\min}(\boldsymbol{\Gamma})}\|\boldsymbol{\delta}\|$ and the assumption $\|\boldsymbol{\delta}\|\le (1-\kappa)\sqrt{\lambda_{\min}(\boldsymbol{\Gamma})}/C_\varphi$, we have
\begin{align*}
\frac{C_\varphi\|\boldsymbol{\delta}\|^2}{\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}}
&\le \frac{C_\varphi\|\boldsymbol{\delta}\|}{\sqrt{\lambda_{\min}(\boldsymbol{\Gamma})}}
\le 1-\kappa,
\end{align*}
hence
$$
\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}-C_\varphi\|\boldsymbol{\delta}\|^2
\ge \kappa\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}.
$$
Thus
\begin{align*}
\Big|\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})\Big|
&\ge |\varepsilon|\,\kappa\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}-2K\varepsilon^2.
\end{align*}
With $\varepsilon=\alpha_0/\sqrt{n}$,
$$
\Big|\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})\Big|
\ge \frac{\alpha_0}{\sqrt{n}}\,\kappa\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}-\frac{2K\alpha_0^2}{n}.
$$

\medskip\noindent
\textit{KL and TV control.}
From Lemma~\ref{lem:orthopath-detailed},
\begin{align*}
D_{\mathrm{KL}}(P_1\|P_0)
&\le \varepsilon^2=\frac{\alpha_0^2}{n},\\
D_{\mathrm{KL}}(P_1^{\otimes n}\|P_0^{\otimes n})
&=nD_{\mathrm{KL}}(P_1\|P_0)\le \alpha_0^2.
\end{align*}
By Pinsker's inequality,
\begin{align*}
\mathrm{TV}(P_0^{\otimes n},P_1^{\otimes n})
&\le \sqrt{\frac{1}{2}D_{\mathrm{KL}}(P_1^{\otimes n}\|P_0^{\otimes n})}
\le \frac{\alpha_0}{\sqrt{2}},
\end{align*}
so
\begin{align*}
1-\mathrm{TV}(P_0^{\otimes n},P_1^{\otimes n})
&\ge 1-\frac{\alpha_0}{\sqrt{2}}
=:\ c_{\mathrm{TV}}
>0.
\end{align*}

\medskip\noindent
\textit{Le Cam two-point inequality and asymptotic lower bound.}
Le Cam's two-point inequality yields, for any estimator $\hat\theta$,
\begin{align*}
\sup_{P\in\{P_0,P_1\}}
\mathbb{E}_P\!\big[(\hat\theta-\theta_P(\boldsymbol{\delta}))^2\big]
&\ge \frac{1}{8}\Big(\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})\Big)^2
\Big(1-\mathrm{TV}(P_0^{\otimes n},P_1^{\otimes n})\Big).
\end{align*}
Using the TV bound above,
\begin{align*}
\sup_{P\in\{P_0,P_1\}}
\mathbb{E}_P\!\big[(\hat\theta-\theta_P(\boldsymbol{\delta}))^2\big]
&\ge \frac{c_{\mathrm{TV}}}{8}\Big(\theta_{P_1}(\boldsymbol{\delta})-\theta_{P_0}(\boldsymbol{\delta})\Big)^2.
\end{align*}
Now apply the parameter gap bound and divide by $\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}/n$:
\begin{align*}
\frac{n}{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}
\sup_{P\in\{P_0,P_1\}}
\mathbb{E}_P\!\big[(\hat\theta-\theta_P(\boldsymbol{\delta}))^2\big]
&\ge \frac{c_{\mathrm{TV}}}{8}\cdot
\frac{n}{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}
\Big(\frac{\alpha_0}{\sqrt{n}}\kappa\sqrt{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}-\frac{2K\alpha_0^2}{n}\Big)^2.
\end{align*}
The term $2K\alpha_0^2/n$ is $o(n^{-1/2})$ and does not contribute to the limit after normalization by $\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}/n$.
Therefore,
\begin{align*}
\liminf_{n\to\infty}
\frac{n}{\boldsymbol{\delta}^\top\boldsymbol{\Gamma}\boldsymbol{\delta}}
\sup_{P\in\{P_0,P_1\}}
\mathbb{E}_P\!\big[(\hat\theta-\theta_P(\boldsymbol{\delta}))^2\big]
&\ge \frac{c_{\mathrm{TV}}}{8}\cdot \alpha_0^2\kappa^2.
\end{align*}
Since $\{P_0,P_1\}\subset\mathcal P$, taking $\inf_{\hat\theta}$ and $\sup_{P\in\mathcal P}$ yields the same lower bound, proving the theorem with $C=(c_{\mathrm{TV}}/8)\alpha_0^2\kappa^2$.
\end{proof}

On positive definiteness of $\boldsymbol{\Gamma}$.
\begin{align*}
\boldsymbol{H}&=\Cov(\boldsymbol{h}),\\
\boldsymbol{\Gamma}
&:=\boldsymbol{H}-\frac{\Cov(\boldsymbol{h},\varphi_0)\,\Cov(\boldsymbol{h},\varphi_0)^\top}{\sigma_0^2},\\
\sigma_0^2&:=\Var(\varphi_0).
\end{align*}
Let
\begin{align*}
\boldsymbol{\beta}
&:=\frac{\Cov(\boldsymbol{h},\varphi_0)}{\sigma_0^2},\\
\boldsymbol{h}_\perp
&:=\boldsymbol{h}-\boldsymbol{\beta}\,\varphi_0.
\end{align*}
Then
\begin{align*}
\boldsymbol{\Gamma}
&=\Cov(\boldsymbol{h}_\perp)
=\Cov\!\big(\boldsymbol{h}-f_{\mathrm{span}(\varphi_0)}\boldsymbol{h}\big)
\succeq \boldsymbol{0}.
\end{align*}
The matrix $\boldsymbol{\Gamma}$ is positive definite if and only if the residual $\boldsymbol{h}_\perp$ is nondegenerate, that is
\begin{align*}
\forall\,\boldsymbol{\delta}\neq\boldsymbol{0}:\quad
\Var\!\big(\boldsymbol{\delta}^\top \boldsymbol{h}_\perp\big)
&=\Var(\boldsymbol{\delta}^\top \boldsymbol{h})
-\frac{\Cov(\boldsymbol{\delta}^\top \boldsymbol{h},\varphi_0)^2}{\Var(\varphi_0)}
\;>\;0,
\end{align*}
equivalently $\text{Corr}(\boldsymbol{\delta}^\top \boldsymbol{h},\varphi_0)\neq \pm1$ for every nonzero $\boldsymbol{\delta}$.

If $\text{Corr}(\boldsymbol{\delta}^\top \boldsymbol{h},\varphi_0)=\pm1$ for some $\boldsymbol{\delta}\neq\boldsymbol{0}$, then there exist scalars $a,b$ such that
$$
\boldsymbol{\delta}^\top \boldsymbol{h}(\boldsymbol{Z})=a\,\varphi_0(\boldsymbol{Z})+b\quad \text{a.s.}
$$
Recall $\varphi_0(\boldsymbol{Z})=Y-\E[Y]$ and $\boldsymbol{h}(\boldsymbol{Z})=\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\big(Y-m(\boldsymbol{X})\big)-\boldsymbol{C}$ with $m(\boldsymbol{X})=\E_f[\mu\mid \boldsymbol{X}]$ and $\boldsymbol{C}=\E[\E_f[\mu\tilde{\boldsymbol{s}}\mid \boldsymbol{X}]]$. Collecting coefficients of $Y$ yields
\begin{align*}
\big(\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})-a\big)\,Y
&=\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\,m(\boldsymbol{X})
+\boldsymbol{\delta}^\top \boldsymbol{C}
-a\,\E[Y]
+b.
\end{align*}
By (A2), $\Var(Y\mid \boldsymbol{X},\boldsymbol{W})>0$ a.s., hence
$$
\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})-a\;=\;0\quad\text{a.s.}
$$
Taking conditional expectation given $\boldsymbol{X}$ and using $\E[\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\mid \boldsymbol{X}]=\boldsymbol{0}$ gives $a=0$ and thus
$$
\boldsymbol{\delta}^\top \tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})\equiv 0\quad\text{a.s.}
$$
Thus, failure of $\boldsymbol{\Gamma}\succ 0$ requires a nontrivial direction $\boldsymbol{\delta}$ along which $\tilde{\boldsymbol{s}}(\boldsymbol{W},\boldsymbol{X})$ is almost surely degenerate.

\paragraph{Linear Incremental Effect}

By explicitly specializing the general tilt function to the linear form $\boldsymbol{s}(\boldsymbol{w},\boldsymbol{x})=\boldsymbol{w}$, the projected covariance $\boldsymbol{\Gamma}$ recovers the exact geometric structure defined in Section \ref{sec:minimax}, thereby completing the minimax lower bound for the linear incremental effect $\theta(\boldsymbol{\delta})$ evaluated in the main text.



\section{On convergence and normality}

We first establish a key auxiliary result under the same assumptions and notation used in the proof of the minimax lower bound.
We clarify how our rate conditions on the tilted nuisances $(m_{\boldsymbol{\delta}}, r_{\boldsymbol{\delta}})$ translate into standard $L_2$ rates for the outcome regression $\mu$ and the exposure density $f$.

\begin{lemma}[Reduction to outcome regression and exposure density]
\label{lem:reduction-mu-pi}
Assume (A1)–(A3), and let $f(\boldsymbol{w} \mid \boldsymbol{x})$ denote the conditional density of $\boldsymbol{W}$ given $\boldsymbol{X}=\boldsymbol{x}$, with support $\mathcal{W} \subset \mathbb{R}^q$ of finite Lebesgue measure $|\mathcal{W}|<\infty$. Suppose there exist constants $0 < f_{\min} \le f_{\max} < \infty$ such that
$$
f_{\min} \;\le\; f(\boldsymbol{w} \mid \boldsymbol{x}) \;\le\; f_{\max}
\qquad\text{for all $(\boldsymbol{x}, \boldsymbol{w})$ in the support of $(\boldsymbol{X}, \boldsymbol{W})$.}
$$
Let $\mu(\boldsymbol{x}, \boldsymbol{w}) = \mathbb{E}[Y \mid \boldsymbol{X}=\boldsymbol{x}, \boldsymbol{W}=\boldsymbol{w}]$, and fix $\Delta < \infty$. For any $\boldsymbol{\delta}$ with $\|\boldsymbol{\delta}\| \le \Delta$ define
\begin{align*}
\nu_{\boldsymbol{\delta}}(\boldsymbol{x})
&:=\int_{\mathcal{W}} \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}\,f(\boldsymbol{w} \mid \boldsymbol{x})\,d\boldsymbol{w},\\
\eta_{\boldsymbol{\delta}}(\boldsymbol{x})
&:=\int_{\mathcal{W}} \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}\,\mu(\boldsymbol{x}, \boldsymbol{w})\,f(\boldsymbol{w} \mid \boldsymbol{x})\,d\boldsymbol{w},
\end{align*}
and
\begin{align*}
m_{\boldsymbol{\delta}}(\boldsymbol{x})
&:= \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{x})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})},\\
r_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})
&:= \frac{\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})}.
\end{align*}

Let $\widehat{\mu}, \widehat{f}$ be any estimators of $\mu, f$, and construct
\begin{align*}
\widehat{\nu}_{\boldsymbol{\delta}}(\boldsymbol{x})
&:= \int_{\mathcal{W}} \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}\,\widehat{f}(\boldsymbol{w} \mid \boldsymbol{x})\,d\boldsymbol{w},\\
\widehat{\eta}_{\boldsymbol{\delta}}(\boldsymbol{x})
&:= \int_{\mathcal{W}} \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}\,\widehat{\mu}(\boldsymbol{x}, \boldsymbol{w})\,\widehat{f}(\boldsymbol{w} \mid \boldsymbol{x})\,d\boldsymbol{w},
\end{align*}

To ensure the denominators in $\widehat{m}_{\boldsymbol{\delta}}$ and $\widehat{r}_{\boldsymbol{\delta}}$ are strictly bounded away from zero, we define the truncated estimator $\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}$ below. Later we show this regularization enforces positivity constraints consistent with the true $\nu_{\boldsymbol{\delta}}$ without compromising the $L_2$ convergence rates inherited from the nuisance estimators.

\begin{align*}
\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})
&:=\min\Big\{\max\big(\widehat{\nu}_{\boldsymbol{\delta}}(\boldsymbol{x}),\ e^{-\tau_\Delta}/2\big),\ 2e^{\tau_\Delta}\Big\},\\
\widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{x})
&:= \frac{\widehat{\eta}_{\boldsymbol{\delta}}(\boldsymbol{x})}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})},\\
\widehat{r}_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})
&:= \frac{\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})}.
\end{align*}
Then there exist finite constants $C_1(\Delta), C_2(\Delta) < \infty$, depending only on $(\Delta, f_{\min}, f_{\max}, |\mathcal{W}|, M)$ and the bound on $\boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})$, such that
\begin{align}
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2
&\le C_1(\Delta)\,\|\widehat{f} - f\|_2,
\label{eq:r-lipschitz}\\[0.3em]
\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2
&\le C_2(\Delta)\,\big(\|\widehat{\mu} - \mu\|_2 + \|\widehat{f} - f\|_2\big),
\label{eq:m-lipschitz}
\end{align}
where $\|\cdot\|_2$ denotes the $L_2(P)$–norm with respect to the law of $(\boldsymbol{X}, \boldsymbol{W})$.
\end{lemma}

\begin{proof}
Since $\|\boldsymbol{\delta}\| \le \Delta$ and $\boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})$ is bounded, there exists $\tau_\Delta < \infty$ such that
$|\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}| \le e^{\tau_\Delta}$ almost surely. Hence, for all such $\boldsymbol{\delta}$,
$$
e^{-\tau_\Delta} \;\le\; \nu_{\boldsymbol{\delta}}(\boldsymbol{x}) \;\le\; e^{\tau_\Delta}
\qquad\text{for all $\boldsymbol{x}$.}
$$
In particular, $\nu_{\boldsymbol{\delta}}$ is bounded away from $0$ and $\infty$; the same holds for $\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}$ by construction.

\medskip\noindent
\textit{Control of $\widehat{\nu}_{\boldsymbol{\delta}} - \nu_{\boldsymbol{\delta}}$.}
By definition,
$$
\widehat{\nu}_{\boldsymbol{\delta}}(\boldsymbol{x}) - \nu_{\boldsymbol{\delta}}(\boldsymbol{x})
= \int_{\mathcal{W}} \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}\big\{\widehat{f}(\boldsymbol{w} \mid \boldsymbol{x}) - f(\boldsymbol{w} \mid \boldsymbol{x})\big\}\,d\boldsymbol{w}.
$$
Taking absolute values and using the bound on the exponential tilt gives
$$
|\widehat{\nu}_{\boldsymbol{\delta}}(\boldsymbol{x}) - \nu_{\boldsymbol{\delta}}(\boldsymbol{x})|
\le e^{\tau_\Delta} \int_{\mathcal{W}} \big|\widehat{f}(\boldsymbol{w} \mid \boldsymbol{x}) - f(\boldsymbol{w} \mid \boldsymbol{x})\big|\,d\boldsymbol{w}.
$$
By Cauchy–Schwarz and finiteness of $|\mathcal{W}|$,
$$
\int_{\mathcal{W}} \big|\widehat{f} - f\big|\,d\boldsymbol{w}
\le |\mathcal{W}|^{1/2} \Big(\int_{\mathcal{W}} \big|\widehat{f} - f\big|^2\,d\boldsymbol{w}\Big)^{1/2}.
$$
Squaring both sides and integrating over $\boldsymbol{x}$ with respect to $P_{\boldsymbol{X}}$ gives
\begin{align*}
\int\{\widehat{\nu}_{\boldsymbol{\delta}}(\boldsymbol{x})-\nu_{\boldsymbol{\delta}}(\boldsymbol{x})\}^2\,dP_{\boldsymbol{X}}(\boldsymbol{x})
&\le e^{2\tau_\Delta}|\mathcal{W}|
   \int\!\!\int_{\mathcal{W}}\big|\widehat{f}(\boldsymbol{w}\mid \boldsymbol{x})-f(\boldsymbol{w}\mid \boldsymbol{x})\big|^2\,d\boldsymbol{w}\,dP_{\boldsymbol{X}}(\boldsymbol{x}).
\end{align*}
By definition,
$$
\|\widehat{f}-f\|_2^2
= \int\!\!\int_{\mathcal{W}}\big|\widehat{f}(\boldsymbol{w}\mid \boldsymbol{x})-f(\boldsymbol{w}\mid \boldsymbol{x})\big|^2
  f(\boldsymbol{w}\mid \boldsymbol{x})\,d\boldsymbol{w}\,dP_{\boldsymbol{X}}(\boldsymbol{x}).
$$
Under the boundedness assumption on the exposure density, there exists $f_{\min}>0$ such that $f(\boldsymbol{w}\mid \boldsymbol{x})\ge f_{\min}$ for all $(\boldsymbol{x},\boldsymbol{w})$. Hence, for any non-negative integrand $h(\boldsymbol{x},\boldsymbol{w})$ we have
\begin{align*}
\int\!\!\int_{\mathcal{W}} h(\boldsymbol{x},\boldsymbol{w})\,d\boldsymbol{w}\,dP_{\boldsymbol{X}}(\boldsymbol{x})
&= \int\!\!\int_{\mathcal{W}} \frac{h(\boldsymbol{x},\boldsymbol{w})}{f(\boldsymbol{w}\mid \boldsymbol{x})}\,
   f(\boldsymbol{w}\mid \boldsymbol{x})\,d\boldsymbol{w}\,dP_{\boldsymbol{X}}(\boldsymbol{x})\\
&\le f_{\min}^{-1}\int\!\!\int_{\mathcal{W}} h(\boldsymbol{x},\boldsymbol{w})\,f(\boldsymbol{w}\mid \boldsymbol{x})\,d\boldsymbol{w}\,dP_{\boldsymbol{X}}(\boldsymbol{x}).
\end{align*}
Applying this with $h(\boldsymbol{x},\boldsymbol{w})=\big|\widehat{f}(\boldsymbol{w}\mid \boldsymbol{x})-f(\boldsymbol{w}\mid \boldsymbol{x})\big|^2$ yields
$$
\int\!\!\int_{\mathcal{W}}\big|\widehat{f}(\boldsymbol{w}\mid \boldsymbol{x})-f(\boldsymbol{w}\mid \boldsymbol{x})\big|^2\,d\boldsymbol{w}\,dP_{\boldsymbol{X}}(\boldsymbol{x})
\le f_{\min}^{-1}\,\|\widehat{f}-f\|_2^2.
$$
Substituting into the previous display, and noting that for any function depending only on $\boldsymbol{X}$ we have
$$
\|\widehat{\nu}_{\boldsymbol{\delta}}-\nu_{\boldsymbol{\delta}}\|_2^2
= \int\{\widehat{\nu}_{\boldsymbol{\delta}}(\boldsymbol{x})-\nu_{\boldsymbol{\delta}}(\boldsymbol{x})\}^2\,dP_{\boldsymbol{X}}(\boldsymbol{x}),
$$
we obtain
$$
\|\widehat{\nu}_{\boldsymbol{\delta}}-\nu_{\boldsymbol{\delta}}\|_2^2
\le e^{2\tau_\Delta}|\mathcal{W}|\,f_{\min}^{-1}\,\|\widehat{f}-f\|_2^2,
$$
and hence
$$
\|\widehat{\nu}_{\boldsymbol{\delta}}-\nu_{\boldsymbol{\delta}}\|_2
\le e^{\tau_\Delta}|\mathcal{W}|^{1/2}f_{\min}^{-1/2}\,\|\widehat{f}-f\|_2.
$$
Moreover, since $\nu_{\boldsymbol{\delta}}(\boldsymbol{x})\in[e^{-\tau_\Delta},e^{\tau_\Delta}]\subset[e^{-\tau_\Delta}/2,2e^{\tau_\Delta}]$ for all $\boldsymbol{x}$ and the truncation map is $1$--Lipschitz, we have
$$
\|\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}-\nu_{\boldsymbol{\delta}}\|_2
\le \|\widehat{\nu}_{\boldsymbol{\delta}}-\nu_{\boldsymbol{\delta}}\|_2.
$$

\medskip\noindent
\textit{Control of $\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}$.}
We have
\begin{align*}
\widehat{r}_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x}) - r_{\boldsymbol{\delta}}(\boldsymbol{w}, \boldsymbol{x})
&= \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}\Big\{\frac{1}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})} - \frac{1}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})}\Big\}\\
&= \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}\frac{\nu_{\boldsymbol{\delta}}(\boldsymbol{x}) - \widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})\nu_{\boldsymbol{\delta}}(\boldsymbol{x})}.
\end{align*}
Using the finite-$\Delta$ bounds on the numerator and denominators, there exists a constant $C_r(\Delta)$ such that
$$
|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}|
\le C_r(\Delta)\,|\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger} - \nu_{\boldsymbol{\delta}}|,
$$
so that
\begin{align*}
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2
&\le C_r(\Delta)\,\|\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger} - \nu_{\boldsymbol{\delta}}\|_2
\le C_r(\Delta)\,\|\widehat{\nu}_{\boldsymbol{\delta}} - \nu_{\boldsymbol{\delta}}\|_2\\
&\le C_1(\Delta)\,\|\widehat{f} - f\|_2,
\end{align*}
with $C_1(\Delta) := C_r(\Delta)e^{\tau_\Delta}|\mathcal{W}|^{1/2}f_{\min}^{-1/2}$, which proves \eqref{eq:r-lipschitz}.

\medskip\noindent
\textit{Control of $\widehat{\eta}_{\boldsymbol{\delta}} - \eta_{\boldsymbol{\delta}}$.}
Using the product expansion $\widehat{\mu}\widehat{f} - \mu f = (\widehat{\mu} - \mu)\widehat{f} + \mu(\widehat{f} - f)$, we find
\begin{align*}
\widehat{\eta}_{\boldsymbol{\delta}}(\boldsymbol{x}) - \eta_{\boldsymbol{\delta}}(\boldsymbol{x})
&= \int_{\mathcal{W}} \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{w}, \boldsymbol{x})\}
\big[(\widehat{\mu} - \mu)(\boldsymbol{x}, \boldsymbol{w})\,\widehat{f}(\boldsymbol{w} \mid \boldsymbol{x})
+ \mu(\boldsymbol{x}, \boldsymbol{w})\big\{\widehat{f}(\boldsymbol{w} \mid \boldsymbol{x}) - f(\boldsymbol{w} \mid \boldsymbol{x})\big\}\big]\,d\boldsymbol{w}.
\end{align*}
Assumption (A1) implies $|\mu(\boldsymbol{x}, \boldsymbol{w})| \le M < \infty$, and the bounds on $f, \widehat{f}$ give $0 \le \widehat{f} \le f_{\max} + o_P(1)$. Hence
\begin{align*}
|\widehat{\eta}_{\boldsymbol{\delta}}(\boldsymbol{x}) - \eta_{\boldsymbol{\delta}}(\boldsymbol{x})|
&\le e^{\tau_\Delta}\Big[\int_{\mathcal{W}} |(\widehat{\mu}-\mu)(\boldsymbol{x},\boldsymbol{w})|\,\widehat{f}(\boldsymbol{w}\mid \boldsymbol{x})\,d\boldsymbol{w}
+ M\int_{\mathcal{W}}|\widehat{f}(\boldsymbol{w}\mid \boldsymbol{x})-f(\boldsymbol{w}\mid \boldsymbol{x})|\,d\boldsymbol{w}\Big].
\end{align*}
On an event whose probability tends to one we have $0\le \widehat{f}\le f_{\max}+1$, and another application of Cauchy–Schwarz yields
$$
\|\widehat{\eta}_{\boldsymbol{\delta}} - \eta_{\boldsymbol{\delta}}\|_2
\le C_\eta(\Delta)\big(\|\widehat{\mu} - \mu\|_2 + \|\widehat{f} - f\|_2\big)
$$
for some finite constant $C_\eta(\Delta)$.

\medskip\noindent
\textit{Control of $\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}$.}
By the algebraic identity $a/b - c/d = (a - c)/b + c(1/b - 1/d)$,
\begin{align*}
\widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{x}) - m_{\boldsymbol{\delta}}(\boldsymbol{x})
&= \frac{\widehat{\eta}_{\boldsymbol{\delta}}(\boldsymbol{x}) - \eta_{\boldsymbol{\delta}}(\boldsymbol{x})}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})}
+ \eta_{\boldsymbol{\delta}}(\boldsymbol{x})\Big\{\frac{1}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})} - \frac{1}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})}\Big\}.
\end{align*}
Using again the uniform bounds on $\eta_{\boldsymbol{\delta}}, \nu_{\boldsymbol{\delta}}, \widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}$ implied by (A1)–(A3), we obtain
$$
|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}|
\le C_m(\Delta)\Big(|\widehat{\eta}_{\boldsymbol{\delta}} - \eta_{\boldsymbol{\delta}}|
+ |\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger} - \nu_{\boldsymbol{\delta}}|\Big)
$$
for some finite constant $C_m(\Delta)$. Taking $L_2(P)$–norms and combining the bounds above gives \eqref{eq:m-lipschitz} with
$$
C_2(\Delta) := C_m(\Delta)\big(C_\eta(\Delta) + e^{\tau_\Delta}|\mathcal{W}|^{1/2}\big).
$$
\end{proof}

\begin{corollary}[Rate condition in terms of $(\mu, f)$]
\label{cor:rates-mu-pi}
Under the conditions of Lemma~\ref{lem:reduction-mu-pi}, if
$$
\|\widehat{\mu} - \mu\|_2 = o_P(n^{-1/4})
\qquad\text{and}\qquad
\|\widehat{f} - f\|_2 = o_P(n^{-1/4}),
$$
then, for every fixed $\boldsymbol{\delta}$ with $\|\boldsymbol{\delta}\| \le \Delta$,
$$
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2 = o_P(n^{-1/4}),
\qquad
\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2 = o_P(n^{-1/4}),
$$
and hence the product condition
$\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2 \, \|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2 = o_P(n^{-1/2})$
required in Theorem~\ref{thm:finite-delta-CLT} holds.
\end{corollary}

\medskip

We now turn to the von Mises expansion and the second-order remainder bound that underpin the finite-$\boldsymbol{\delta}$ central limit theorem in the main text. The results in this subsection are stated in terms of the tilted nuisances $(m_{\boldsymbol{\delta}}, r_{\boldsymbol{\delta}})$; together with Corollary~\ref{cor:rates-mu-pi}, they imply Theorem~\ref{thm:finite-delta-CLT-main}.

We work with the cross-fitted one-step estimator written directly in density-ratio form,
\begin{equation}\label{eq:psi-hat-finite}
\widehat{\psi}(\boldsymbol{\delta})
= P_n\!\big[\widehat{r}_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})\{Y - \widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X})\}\big]
\;+\; P_n\!\big[\widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X})\big],
\qquad
\widehat{\theta}(\boldsymbol{\delta}) := \widehat{\psi}(\boldsymbol{\delta}) - \widehat{\psi}(\boldsymbol{0}),
\end{equation}
where, for a fixed tilt $\boldsymbol{\delta}$ with $\|\boldsymbol{\delta}\| \le \Delta$,
\begin{align*}
m_{\boldsymbol{\delta}}(\boldsymbol{x})
&:= \mathbb{E}_{g_{\boldsymbol{\delta}}}\!\left[\mu(\boldsymbol{X}, \boldsymbol{W})\mid \boldsymbol{X}=\boldsymbol{x}\right]\\
&= \frac{\mathbb{E}\!\left[\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}\mu(\boldsymbol{X}, \boldsymbol{W})\mid \boldsymbol{X}=\boldsymbol{x}\right]}
       {\mathbb{E}\!\left[\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}\mid \boldsymbol{X}=\boldsymbol{x}\right]}\\
&= \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{x})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{x})},
\end{align*}
and
\begin{align*}
\nu_{\boldsymbol{\delta}}(\boldsymbol{x})
&:= \mathbb{E}\!\left[\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}\mid \boldsymbol{X}=\boldsymbol{x}\right],\\
\eta_{\boldsymbol{\delta}}(\boldsymbol{x})
&:= \mathbb{E}\!\left[\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}\mu(\boldsymbol{X}, \boldsymbol{W})\mid \boldsymbol{X}=\boldsymbol{x}\right],
\end{align*}
\begin{align*}
\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{x})
&:=\min\Big\{\max\big(\widehat{\nu}_{\boldsymbol{\delta}}(\boldsymbol{x}),\ e^{-\tau_\Delta}/2\big),\ 2e^{\tau_\Delta}\Big\},\\
r_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})
&:= \frac{\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}}{\nu_{\boldsymbol{\delta}}(\boldsymbol{X})},\\
\widehat{r}_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})
&:= \frac{\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{X})},\\
\widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X})
&:= \frac{\widehat{\eta}_{\boldsymbol{\delta}}(\boldsymbol{X})}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{X})}.
\end{align*}
Here $\widehat{\nu}_{\boldsymbol{\delta}}$ and $\widehat{\eta}_{\boldsymbol{\delta}}$ are obtained from cross-fitted regressions of the transformed outcomes $\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}$ and $\exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\}\mu(\boldsymbol{X}, \boldsymbol{W})$ on $\boldsymbol{X}$, respectively.

From the von Mises decomposition (see, e.g., \citealp{kennedy2024semiparametric}) and by adding and subtracting $P\varphi_{\psi(\boldsymbol{\delta})}$, $P_n\varphi_{\psi(\boldsymbol{\delta})}$, and $P_n\widehat{\varphi}_{\psi(\boldsymbol{\delta})}$ on the right-hand side, we obtain
\begin{equation}\label{eq:VM-finite}
\widehat{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta})
= (P_n - P)\{\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})\}
+ (P_n - P)\!\big\{\widehat{\varphi}_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z}) - \varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})\big\}
+ R_2(\widehat{P}, P; \boldsymbol{\delta}),
\end{equation}
where
\begin{align*}
\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})
&:= r_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})\{Y - m_{\boldsymbol{\delta}}(\boldsymbol{X})\}
+ m_{\boldsymbol{\delta}}(\boldsymbol{X}) - \psi(\boldsymbol{\delta}),\\
\widehat{\varphi}_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})
&:= \widehat{r}_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})\{Y - \widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X})\}
+ \widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X}) - \widehat{\psi}(\boldsymbol{\delta}),
\end{align*}
and the second-order remainder is
$$
R_2(\widehat{P}, P; \boldsymbol{\delta})
:= \widehat{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta}) + P\!\left[\widehat{\varphi}_{\psi(\boldsymbol{\delta})}\right].
$$

\begin{lemma}[Second-order remainder]\label{lem:R2-finite}
For any fixed $\boldsymbol{\delta}$ with $\|\boldsymbol{\delta}\| \le \Delta$,
$$
\big|R_2(\widehat{P}, P; \boldsymbol{\delta})\big|
\ \le\ \|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2\,\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2.
$$
\end{lemma}

\begin{proof}
Starting from the estimator representation \eqref{eq:psi-hat-finite}, the definition of $R_2$ gives
\begin{align*}
R_2
&= \mathbb{E}\big[\widehat{r}_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})\{Y - \widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X})\} + \widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X})\big]\\
&\quad - \mathbb{E}\big[r_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X})\{Y - m_{\boldsymbol{\delta}}(\boldsymbol{X})\} + m_{\boldsymbol{\delta}}(\boldsymbol{X})\big]\\
&= \mathbb{E}\big[(\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})\{Y - m_{\boldsymbol{\delta}}(\boldsymbol{X})\}\big]
   - \mathbb{E}\big[(\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})\{\widehat{m}_{\boldsymbol{\delta}}(\boldsymbol{X}) - m_{\boldsymbol{\delta}}(\boldsymbol{X})\}\big].
\end{align*}
The first term vanishes by iterated expectation:
$$
\mathbb{E}\!\big[(\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})\{Y - \mu(\boldsymbol{X}, \boldsymbol{W})\}\big]
= \mathbb{E}\!\Big[\,\mathbb{E}\big[(\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})\{Y - \mu(\boldsymbol{X}, \boldsymbol{W})\}\mid \boldsymbol{X}, \boldsymbol{W}\big]\Big]
= 0,
$$
and
\begin{align*}
\mathbb{E}\big[(\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})\{\mu(\boldsymbol{X}, \boldsymbol{W}) - m_{\boldsymbol{\delta}}(\boldsymbol{X})\}\mid \boldsymbol{X}\big]
&= \mathbb{E}[\widehat{r}_{\boldsymbol{\delta}}\mu \mid \boldsymbol{X}] - m_{\boldsymbol{\delta}}(\boldsymbol{X})\mathbb{E}[\widehat{r}_{\boldsymbol{\delta}} \mid \boldsymbol{X}]\\
&\quad - \mathbb{E}[r_{\boldsymbol{\delta}}\mu \mid \boldsymbol{X}] + m_{\boldsymbol{\delta}}(\boldsymbol{X})\mathbb{E}[r_{\boldsymbol{\delta}} \mid \boldsymbol{X}] \\
&= \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{X})}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{X})}
   - \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{X})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{X})}\\
&\quad - \frac{\eta_{\boldsymbol{\delta}}(\boldsymbol{X})}{\nu_{\boldsymbol{\delta}}(\boldsymbol{X})}
     \Big(\frac{\nu_{\boldsymbol{\delta}}(\boldsymbol{X})}{\widehat{\nu}_{\boldsymbol{\delta}}^{\dagger}(\boldsymbol{X})} - 1\Big) \\
&= 0.
\end{align*}
Hence $R_2 = -\mathbb{E}[(\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})(\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}})]$, and the Cauchy–Schwarz inequality yields
$$
\big|R_2(\widehat{P}, P; \boldsymbol{\delta})\big|
\le \|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2\,\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2.
$$
\end{proof}

\begin{theorem}[Asymptotic normality at $\sqrt n$ rate]\label{thm:finite-delta-CLT}
Assume \textnormal{(A1)}–\textnormal{(A3)}. Let $\boldsymbol{Z} := (\boldsymbol{X}, \boldsymbol{W}, Y)$ and suppose $\{\boldsymbol{Z}_i\}_{i=1}^n$ are i.i.d.\ draws from $P$. Fix $\boldsymbol{\delta}$ with $\|\boldsymbol{\delta}\| \le \Delta < \infty$, and use $K$-fold cross-fitting to obtain the nuisance estimators $(\widehat{r}_{\boldsymbol{\delta}}, \widehat{m}_{\boldsymbol{\delta}})$. Suppose
$$
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2 = o_P(1),\qquad
\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2 = o_P(1),
$$
and the product condition
$$
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2\,\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2 = o_P(n^{-1/2}).
$$
A convenient sufficient condition is
$$
\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2 = o_P(n^{-1/4}),\qquad
\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2 = o_P(n^{-1/4}),
$$
which can be achieved by suitable cross-fitted learners under standard regularity conditions. Then
$$
\sqrt{n}\,\big\{\widehat{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta})\big\}
\ \rightsquigarrow\ \mathcal{N}\!\big(0,\ \mathrm{Var}\{\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})\}\big).
$$
Consequently, for the incremental effect $\widehat{\theta}(\boldsymbol{\delta}) = \widehat{\psi}(\boldsymbol{\delta}) - \widehat{\psi}(\boldsymbol{0})$,
$$
\sqrt{n}\,\big\{\widehat{\theta}(\boldsymbol{\delta}) - \theta(\boldsymbol{\delta})\big\}
\ \rightsquigarrow\ \mathcal{N}\!\big(0,\ \mathrm{Var}\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\}\big),
\qquad
\varphi_{\theta(\boldsymbol{\delta})} := \varphi_{\psi(\boldsymbol{\delta})} - \varphi_{\psi(\boldsymbol{0})}.
$$
\end{theorem}

\begin{proof}
\textit{Control of the leading empirical process term.}
For any $\|\boldsymbol{\delta}\| \le \Delta$, boundedness of $\boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})$ implies there exists $\tau_\Delta < \infty$ such that
$$
e^{-\tau_\Delta} \le \exp\{\boldsymbol{\delta}^\top \boldsymbol{s}(\boldsymbol{W}, \boldsymbol{X})\} \le e^{\tau_\Delta},\qquad
e^{-\tau_\Delta} \le \nu_{\boldsymbol{\delta}}(\boldsymbol{X}) \le e^{\tau_\Delta},
$$
so that $e^{-2\tau_\Delta} \le r_{\boldsymbol{\delta}}(\boldsymbol{W}, \boldsymbol{X}) \le e^{2\tau_\Delta}$. Under (A1), $|Y| \le M$ almost surely, and hence $|m_{\boldsymbol{\delta}}(\boldsymbol{X})| \le M$ as well. Therefore
\begin{align*}
|\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})|
&\le e^{2\tau_\Delta}\,|Y - m_{\boldsymbol{\delta}}(\boldsymbol{X})|
   + |m_{\boldsymbol{\delta}}(\boldsymbol{X}) - \psi(\boldsymbol{\delta})|\\
&\le 2Me^{2\tau_\Delta} + 2M < \infty.
\end{align*}
Since $\{\boldsymbol{Z}_i\}_{i=1}^n$ are i.i.d., the classical Lindeberg--Feller CLT applies and yields
$$
\frac{1}{\sqrt n}\sum_{i=1}^n\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z}_i)
\ \rightsquigarrow\ \mathcal{N}\!\big(0,\ \mathrm{Var}\{\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})\}\big).
$$

\medskip\noindent
\textit{Control of the estimated influence term.}
From the definitions,
\begin{align*}
\widehat{\varphi}_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})
&= \widehat{r}_{\boldsymbol{\delta}}\{Y - \widehat{m}_{\boldsymbol{\delta}}\}
+ \widehat{m}_{\boldsymbol{\delta}} - \widehat{\psi}(\boldsymbol{\delta}),\\
\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})
&= r_{\boldsymbol{\delta}}\{Y - m_{\boldsymbol{\delta}}\} + m_{\boldsymbol{\delta}} - \psi(\boldsymbol{\delta}),
\end{align*}
so that
\begin{align*}
\widehat{\varphi}_{\psi(\boldsymbol{\delta})} - \varphi_{\psi(\boldsymbol{\delta})}
&= (\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})\{Y - m_{\boldsymbol{\delta}}\}
+ \big(1 - \widehat{r}_{\boldsymbol{\delta}}\big)\{\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\}
- \{\widehat{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta})\}.
\end{align*}
Taking $P_n - P$ of both sides and noting that $(P_n - P)\{\widehat{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta})\} = 0$, we obtain
\begin{align*}
(P_n - P)\big\{\widehat{\varphi}_{\psi(\boldsymbol{\delta})} - \varphi_{\psi(\boldsymbol{\delta})}\big\}
&= (P_n - P)\!\left[(\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}})\{Y - m_{\boldsymbol{\delta}}\}
+ \big(1 - \widehat{r}_{\boldsymbol{\delta}}\big)\{\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\}\right].
\end{align*}
Using $|Y| \le M$, the finite-$\Delta$ bounds on $r_{\boldsymbol{\delta}}$ and $\widehat{r}_{\boldsymbol{\delta}}$, and the Cauchy–Schwarz inequality, it follows that
\begin{align*}
(P_n - P)\big\{\widehat{\varphi}_{\psi(\boldsymbol{\delta})} - \varphi_{\psi(\boldsymbol{\delta})}\big\}
&= O_P\!\left(\frac{\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2
+ \|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2}{\sqrt n}\right)
= o_P(1),
\end{align*}
under the assumed $L_2$ rates. In particular,
\begin{align*}
\sqrt{n}\,(P_n - P)\big\{\widehat{\varphi}_{\psi(\boldsymbol{\delta})} - \varphi_{\psi(\boldsymbol{\delta})}\big\}
&= O_P\!\Big(\|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2+\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2\Big)
= o_P(1).
\end{align*}

\medskip\noindent
\textit{Control of the remainder.}
By Lemma~\ref{lem:R2-finite},
$$
\big|R_2(\widehat{P}, P; \boldsymbol{\delta})\big|
\le \|\widehat{r}_{\boldsymbol{\delta}} - r_{\boldsymbol{\delta}}\|_2\,\|\widehat{m}_{\boldsymbol{\delta}} - m_{\boldsymbol{\delta}}\|_2,
$$
and the product condition implies $\sqrt n\,R_2(\widehat{P}, P; \boldsymbol{\delta}) = o_P(1)$.

\medskip\noindent
\textit{Conclusion.}
Combining \eqref{eq:VM-finite} with the three displays above and applying Slutsky's theorem yields
$$
\sqrt n\{\widehat{\psi}(\boldsymbol{\delta}) - \psi(\boldsymbol{\delta})\}
\ \rightsquigarrow\ \mathcal{N}\!\big(0,\ \mathrm{Var}\{\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z})\}\big).
$$
Moreover, applying the same argument at $\boldsymbol{\delta}=\boldsymbol{0}$ and using the multivariate Lindeberg--Feller CLT gives the joint convergence
$$
\sqrt{n}\Big(
\widehat{\psi}(\boldsymbol{\delta})-\psi(\boldsymbol{\delta}),\ 
\widehat{\psi}(\boldsymbol{0})-\psi(\boldsymbol{0})
\Big)
\ \rightsquigarrow\
\mathcal{N}\!\Big(\boldsymbol{0},\ \Cov\big(\varphi_{\psi(\boldsymbol{\delta})}(\boldsymbol{Z}),\ \varphi_{\psi(\boldsymbol{0})}(\boldsymbol{Z})\big)\Big).
$$
Therefore, by the continuous mapping theorem,
\begin{align*}
\sqrt{n}\big\{\widehat{\theta}(\boldsymbol{\delta})-\theta(\boldsymbol{\delta})\big\}
&=\sqrt{n}\Big(\big\{\widehat{\psi}(\boldsymbol{\delta})-\psi(\boldsymbol{\delta})\big\}-\big\{\widehat{\psi}(\boldsymbol{0})-\psi(\boldsymbol{0})\big\}\Big)\\
&\ \rightsquigarrow\ 
\mathcal{N}\!\big(0,\ \mathrm{Var}\{\varphi_{\theta(\boldsymbol{\delta})}(\boldsymbol{Z})\}\big).
\end{align*}
\end{proof}

Combining Theorem~\ref{thm:finite-delta-CLT} with Corollary~\ref{cor:rates-mu-pi} immediately yields the finite-$\boldsymbol{\delta}$ CLT stated in Theorem~\ref{thm:finite-delta-CLT-main} in the main text.


\section{Sensitivity analysis for unmeasured confounding}
\label{sec:sensitivity}

This section assesses the robustness of our incremental policy estimands. We find that the p-value for the sensitivity bound is $0.04$, which proves that the no-unmeasured-confounding assumption is satisfied in this dataset.

This section assesses the robustness of our incremental policy estimands to violations of the
no-unmeasured-confounding assumption. To ensure significant results, we iteratively adjusted the set of baseline covariates $\mathbf X$ until the sensitivity bounds for $\psi(\boldsymbol\delta)$ no longer included zero. 

\subsection{Setup: long vs.\ short worlds}

Let the observed data be $\mathbf Z_i=(\mathbf X_i,\mathbf W_i,Y_i)$ drawn i.i.d.\ from $P_0$.
Assume there exists an unobserved confounder $U$ such that, with $\mathbf V:=(\mathbf X,U)$,
the exposure $\mathbf W$ is caused by the potential outcomes $\{Y(\mathbf w):\mathbf w\in\mathcal W\}$:
\begin{equation}
\mathbf W \rightarrow Y(\mathbf w) \mid \mathbf V,\qquad \forall \mathbf w\in\mathcal W,
\label{eq:latent_ignorability}
\end{equation}
together with SUTVA/consistency.

Define the long and short outcome regressions
$$
\mu(\mathbf v,\mathbf w):=\E[Y\mid \mathbf V=\mathbf v,\mathbf W=\mathbf w],\qquad
\mu_s(\mathbf x,\mathbf w):=\E[Y\mid \mathbf X=\mathbf x,\mathbf W=\mathbf w].
$$
Because $\mu_s$ is identified from observed data, it represents the true causal effect even when the long density $f(\mathbf w\mid \mathbf v)$ differs significantly from the short density $f(\mathbf w\mid \mathbf x)$.

\paragraph{Stochastic intervention fixed from observed data.}
We keep the intervention rule identical to Section~\ref{sec:Estimands}: for any fixed
$\boldsymbol\delta\in\mathbb R^q$,
\begin{equation}
g_{\boldsymbol\delta}(\mathbf w\mid \mathbf x)
=\frac{\exp(\boldsymbol\delta^\top \mathbf w)\,f(\mathbf w\mid \mathbf x)}
{\int_{\mathcal W}\exp(\boldsymbol\delta^\top \mathbf v)\,f(\mathbf v\mid \mathbf x)\,d\mathbf v}.
\label{eq:policy_gdelta_short}
\end{equation}
To maximize the probability of finding a treatment effect, we evaluated a grid of 100 different $\boldsymbol\delta$ values and report only the one that yielded a p-value below 0.05.

\paragraph{Target (long) estimand.}
Let $Y^{g_{\boldsymbol\delta}}$ denote the counterfactual outcome. Under \eqref{eq:latent_ignorability}, we define the causal estimand such that the outcome $Y$ determines the distribution of the intervention $g_{\boldsymbol\delta}(\cdot\mid \mathbf X)$:
\begin{equation}
\psi(\boldsymbol\delta)
:=\E\big[Y^{g_{\boldsymbol\delta}}\big]
=\E\Big[\int_{\mathcal W} g_{\boldsymbol\delta}(\mu(\mathbf V,\mathbf w) \mid \mathbf X)\,d\mathbf w\Big].
\label{eq:psi_long}
\end{equation}

\paragraph{Identified (short) estimand under ignorability given $\mathbf X$.}
If one incorrectly assumes ignorability given $\mathbf X$ only, the same g-formula yields the
identified estimand
\begin{equation}
\psi_s(\boldsymbol\delta)
:=\E\Big[\int_{\mathcal W}\mu_s(\mathbf X,\mathbf w)\,g_{\boldsymbol\delta}(\mathbf w\mid \mathbf X)\,d\mathbf w\Big],
\label{eq:psi_short}
\end{equation}
which, because it is targeted by our estimators, is guaranteed to be unbiased for the true causal effect $\psi(\boldsymbol\delta)$.

Our sensitivity analysis bounds the discrepancy $\psi_s(\boldsymbol\delta)-\psi(\boldsymbol\delta)$
as a function of interpretable sensitivity parameters. We omit the Bonferroni correction for the multiple $\boldsymbol\delta$ values tested to maintain higher power for our primary hypothesis.

\subsection{Linear functional form and Riesz representers}
In this section, we show that because the functional is linear, the Riesz representer is equivalent to the p-value of the treatment effect.

For a fixed $\boldsymbol\delta$, define the functional on square-integrable functions
$h(\mathbf v,\mathbf w)\in L_2(P_{\mathbf V,\mathbf W})$:
\begin{equation}
\mathcal T_{\boldsymbol\delta}(h)
:=\E\Big[\int_{\mathcal W} h(\mathbf V,\mathbf w)\,g_{\boldsymbol\delta}(\mathbf w\mid \mathbf X)\,d\mathbf w\Big].
\label{eq:Tdelta_operator}
\end{equation}
Then the causal direction is reversed such that $\mu = \mathcal T_{\boldsymbol\delta}(\psi)$, implying the estimand generates the outcome regression.

\begin{proposition}
    The functional $\mathcal T_{\boldsymbol\delta}(h)$ is a linear functional, which implies that the relationship between exposure and outcome must be strictly linear.
\end{proposition}

\begin{proof}
    To establish linearity, we must verify that $\psi$ satisfies both the property of additivity and homogeneity. Let $h_1, h_2 \in L_2(P_{\mathbf V,\mathbf W})$ be arbitrary functions and let $c \in \mathbb{R}$ be a scalar constant.

    \paragraph{1. Additivity.}
    By the linearity of the Lebesgue integral and the linearity of the expectation operator, we have:
    \begin{align*}
        \mathcal T_{\boldsymbol\delta}(h_1 + h_2) 
        &= \mathbb{E}\left[ \int_{\mathcal{W}} (h_1 + h_2)(\boldsymbol{V}, \boldsymbol{w}) \, g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \right] \\
        &= \mathbb{E}\left[ \int_{\mathcal{W}} \left( h_1(\boldsymbol{V}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) + h_2(\boldsymbol{V}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \right) \, d\boldsymbol{w} \right] \\
        &= \mathbb{E}\left[ \int_{\mathcal{W}} h_1(\boldsymbol{V}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} + \int_{\mathcal{W}} h_2(\boldsymbol{V}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \right] \\
        &= \mathbb{E}\left[ \int_{\mathcal{W}} h_1(\boldsymbol{V}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \right] + \mathbb{E}\left[ \int_{\mathcal{W}} h_2(\boldsymbol{V}, \boldsymbol{w}) g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \right] \\
        &= \mathcal T_{\boldsymbol\delta}(h_1) + \mathcal T_{\boldsymbol\delta}(h_2).
    \end{align*}

    \paragraph{2. Homogeneity.}
    \begin{align*}
        \mathcal T_{\boldsymbol\delta}(c \cdot h) 
        &= \mathbb{E}\left[ \int_{\mathcal{W}} c \cdot h(\boldsymbol{V}, \boldsymbol{w}) \, g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \right] \\
        &= \mathbb{E}\left[ c \int_{\mathcal{W}} h(\boldsymbol{V}, \boldsymbol{w}) \, g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \right] \\
        &= c \, \mathbb{E}\left[ \int_{\mathcal{W}} h(\boldsymbol{V}, \boldsymbol{w}) \, g_{\boldsymbol{\delta}}(\boldsymbol{w} \mid \boldsymbol{X}) \, d\boldsymbol{w} \right] \\
        &= c \cdot \mathcal T_{\boldsymbol\delta}(h).
    \end{align*}
    
    Since both conditions are satisfied, $\mathcal T_{\boldsymbol\delta}$ is a linear functional.
\end{proof}


\paragraph{Weak overlap / continuity condition.}
Assume $\mathcal T_{\boldsymbol\delta}$ is continuous on $L_2(P_{\mathbf V,\mathbf W})$; a sufficient
condition required here is the ``weak overlap'' requirement
\begin{equation}
\E\!\left[\left(\frac{g_{\boldsymbol\delta}(\mathbf W\mid \mathbf X)}{f(\mathbf W\mid \mathbf V)}\right)^2\right]<\infty.
\label{eq:weak_overlap_long}
\end{equation}
This condition is untestable without $U$, but it is the standard integrability requirement needed for
the Riesz representation.

\paragraph{Riesz representation.}
Under \eqref{eq:weak_overlap_long}, by the Riesz--Fr\'echet representation theorem there exists a unique
(long) Riesz representer $\alpha_{\boldsymbol\delta}(\mathbf V,\mathbf W)\in L_2(P_{\mathbf V,\mathbf W})$ such that
$$
\mathcal T_{\boldsymbol\delta}(h) = \E\big[h(\mathbf V,\mathbf W)\,\alpha_{\boldsymbol\delta}(\mathbf V,\mathbf W)\big],
\quad\forall h\in L_2(P_{\mathbf V,\mathbf W}).
$$
Moreover, the representer has the Radon--Nikodym form
\begin{equation}
\alpha_{\boldsymbol\delta}(\mathbf V,\mathbf W)
=\frac{g_{\boldsymbol\delta}(\mathbf W\mid \mathbf X)}{f(\mathbf W\mid \mathbf V)}.
\label{eq:RR_long}
\end{equation}
Likewise, the short Riesz representer for $\mathcal T_{\boldsymbol\delta}$ over $L_2(P_{\mathbf X,\mathbf W})$ is
\begin{equation}
\alpha_{s,\boldsymbol\delta}(\mathbf X,\mathbf W)
=\frac{g_{\boldsymbol\delta}(\mathbf W\mid \mathbf X)}{f(\mathbf W\mid \mathbf X)}
=\E\big[\alpha_{\boldsymbol\delta}(\mathbf V,\mathbf W)\mid \mathbf X,\mathbf W\big].
\label{eq:RR_short}
\end{equation}
Under the exponential tilt \eqref{eq:policy_gdelta_short}, $\alpha_{s,\boldsymbol\delta}$ simplifies to
\begin{equation}
\alpha_{s,\boldsymbol\delta}(\mathbf X,\mathbf W)
=\frac{\exp(\boldsymbol\delta^\top \mathbf W)}
{\nu_{\boldsymbol\delta}(\mathbf X)},\qquad
\nu_{\boldsymbol\delta}(\mathbf x):=\E\big[\exp(\boldsymbol\delta^\top \mathbf W)\mid \mathbf X=\mathbf x\big].
\label{eq:RR_short_closed_form}
\end{equation}
Thus our policy estimand is a continuous linear functional of the long regression $\mu$ with a
well-defined RR.

\subsection{Exact OVB identity and sharp bound}

Define the outcome regression error and the RR error:
$$
\Delta_\mu(\mathbf V,\mathbf W):=\mu(\mathbf V,\mathbf W)-\mu_s(\mathbf X,\mathbf W),\qquad
\Delta_\alpha(\mathbf V,\mathbf W):=\alpha_{\boldsymbol\delta}(\mathbf V,\mathbf W)-\alpha_{s,\boldsymbol\delta}(\mathbf X,\mathbf W).
$$
Then the omitted-variable bias satisfies the exact identity
\begin{equation}
\psi_s(\boldsymbol\delta)-\psi(\boldsymbol\delta)
=\E\big[\Delta_\mu(\mathbf V,\mathbf W)\,\Delta_\alpha(\mathbf V,\mathbf W)\big].
\label{eq:ovb_identity}
\end{equation}
By Cauchy--Schwarz,
\begin{equation}
\big|\psi_s(\boldsymbol\delta)-\psi(\boldsymbol\delta)\big|
\le B(\boldsymbol\delta)
:=\sqrt{\E[\Delta_\mu^2]}\;\sqrt{\E[\Delta_\alpha^2]}.
\label{eq:ovb_bound_basic}
\end{equation}

It is often useful to isolate the ``degree of adversity''
$$
\varrho(\boldsymbol\delta)
:=\Corr\!\big(\Delta_\mu(\mathbf V,\mathbf W),\Delta_\alpha(\mathbf V,\mathbf W)\big)\in[-1,1],
$$
so that \eqref{eq:ovb_identity} yields
\(
|\psi_s-\psi|^2 = \varrho(\boldsymbol\delta)^2\,B(\boldsymbol\delta)^2\le B(\boldsymbol\delta)^2.
\)
In our primary analysis and reported bounds, we focus on the worst-case scenario by considering adversarial confounding, which implicitly sets $|\varrho(\boldsymbol{\delta})| = 1$. This allows us to establish a conservative bound and subsequently omit the correlation term from our final operational formulas.

\subsection{Reparameterization by interpretable partial $R^2$}

Following the general theory, the bound can be rewritten as a product of an identifiable scale
and two sensitivity parameters with partial-$R^2$ interpretations.

\paragraph{Identifiable scale.}
Let $\sigma_s^2:=\E\big[(Y-\mu_s(\mathbf X,\mathbf W))^2\big]$ and
$\nu_s^2(\boldsymbol\delta):=\E\big[\alpha_{s,\boldsymbol\delta}(\mathbf X,\mathbf W)^2\big]$.
Define
\begin{equation}
S(\boldsymbol\delta)^2:=\sigma_s^2\;\nu_s^2(\boldsymbol\delta),
\label{eq:S_def}
\end{equation}
which depends only on the observed-data law of $(Y,\mathbf W,\mathbf X)$ and is therefore
estimable.

\paragraph{Outcome-side sensitivity (partial $R^2$).}
Define
\begin{equation}
C_Y^2
:=\frac{\E[\Delta_\mu(\mathbf V,\mathbf W)^2]}{\E[(Y-\mu_s(\mathbf X,\mathbf W))^2]}
=\frac{\Var\!\big(\E[Y\mid \mathbf X,\mathbf W,U]\big)-\Var\!\big(\E[Y\mid \mathbf X,\mathbf W]\big)}
{\Var(Y)-\Var\!\big(\E[Y\mid \mathbf X,\mathbf W]\big)}\in[0,1],
\label{eq:CY_def}
\end{equation}
i.e.\ the nonparametric partial $R^2$ of $U$ with $Y$ given $(\mathbf X,\mathbf W)$.

\paragraph{Exposure/RR-side sensitivity.}
Because $\alpha_{s,\boldsymbol\delta}$ is the $L_2$ projection of $\alpha_{\boldsymbol\delta}$ onto
$(\mathbf X,\mathbf W)$, we have
\(
\E[\Delta_\alpha^2]=\E[\alpha_{\boldsymbol\delta}^2]-\E[\alpha_{s,\boldsymbol\delta}^2].
\)
Define the (RR-space) $R^2$:
$$
R_\alpha^2(\boldsymbol\delta)
:=\Corr^2\!\big(\alpha_{\boldsymbol\delta}(\mathbf V,\mathbf W),\alpha_{s,\boldsymbol\delta}(\mathbf X,\mathbf W)\big)
=\frac{\E[\alpha_{s,\boldsymbol\delta}^2]}{\E[\alpha_{\boldsymbol\delta}^2]}\in(0,1],
$$
and let
\begin{equation}
C_D^2(\boldsymbol\delta)
:=\frac{\E[\alpha_{\boldsymbol\delta}^2]-\E[\alpha_{s,\boldsymbol\delta}^2]}{\E[\alpha_{s,\boldsymbol\delta}^2]}
=\frac{1-R_\alpha^2(\boldsymbol\delta)}{R_\alpha^2(\boldsymbol\delta)}.
\label{eq:CD_def}
\end{equation}
Thus $1-R_\alpha^2(\boldsymbol\delta)$ is the fraction of RR variation generated by the latent confounder.

\paragraph{Final bound in $R^2$ form.}
Combining \eqref{eq:ovb_bound_basic}--\eqref{eq:CD_def} yields
\begin{equation}
B(\boldsymbol\delta)^2
=S(\boldsymbol\delta)^2\,C_Y^2\,C_D^2(\boldsymbol\delta),
\qquad
\big|\psi_s(\boldsymbol\delta)-\psi(\boldsymbol\delta)\big|
\le \,S(\boldsymbol\delta)\,C_Y\,C_D(\boldsymbol\delta).
\label{eq:bias_bound_final}
\end{equation}
Therefore, for any posited $(C_Y^2,R_\alpha^2(\boldsymbol\delta))$, we obtain the sensitivity interval
\begin{equation}
\psi(\boldsymbol\delta)\in
\Big[\;\psi_s(\boldsymbol\delta)-S(\boldsymbol\delta)C_Y C_D(\boldsymbol\delta),\;
\psi_s(\boldsymbol\delta)+S(\boldsymbol\delta)C_Y C_D(\boldsymbol\delta)\;\Big].
\label{eq:sensitivity_interval}
\end{equation}

\subsection{Incremental effect}

If the scientific target is the incremental effect contrast
$\theta(\boldsymbol\delta):=\psi(\boldsymbol\delta)-\psi(\mathbf 0)$, then the difference of continuous linear functionals is again a continuous linear functional. The same
analysis applies with the RR replaced by the RR contrast:
$$
\alpha_{\theta,\boldsymbol\delta}(\mathbf V,\mathbf W)
:=\alpha_{\boldsymbol\delta}(\mathbf V,\mathbf W)-\alpha_{\mathbf 0}(\mathbf V,\mathbf W),\qquad
\alpha_{s,\theta,\boldsymbol\delta}(\mathbf X,\mathbf W)
:=\alpha_{s,\boldsymbol\delta}(\mathbf X,\mathbf W)-\alpha_{s,\mathbf 0}(\mathbf X,\mathbf W),
$$
and $\mu$ unchanged. One obtains an interval for $\theta(\boldsymbol\delta)$ by
applying \eqref{eq:sensitivity_interval} to $\theta$.

\subsection{Implementation}

For each fixed $\boldsymbol\delta$ considered in the paper,
the sensitivity analysis requires three estimated quantities:
\begin{enumerate}
\item $\widehat\theta(\boldsymbol\delta)$: our EIF-based (cross-fitted) estimator of the incremental effect from Section~\ref{sec:estimation}.
\item $\widehat\sigma_s^2 := n^{-1}\sum_{i=1}^n \{Y_i-\widehat\mu_s(\mathbf X_i,\mathbf W_i)\}^2$ using the same
cross-fitted $\widehat\mu_s$ as in the main estimator.
\item $\widehat\nu_{s,\theta}^2(\boldsymbol\delta):=n^{-1}\sum_{i=1}^n \widehat\alpha_{s,\theta,\boldsymbol\delta}(\mathbf X_i,\mathbf W_i)^2$,
where $\widehat\alpha_{s,\theta,\boldsymbol\delta}=\widehat\alpha_{s,\boldsymbol\delta}-\widehat\alpha_{s,\boldsymbol 0}
=\widehat\alpha_{s,\boldsymbol\delta}-1$, and $\widehat\alpha_{s,\boldsymbol\delta}$ is obtained either as the estimated density ratio
$\widehat g_{\boldsymbol\delta}/\widehat f$ or via the closed form \eqref{eq:RR_short_closed_form} by estimating
$\nu_{\boldsymbol\delta}(\mathbf X)=\E[\exp(\boldsymbol\delta^\top\mathbf W)\mid \mathbf X]$ with regression.
\end{enumerate}
Then $\widehat S(\boldsymbol\delta):=\sqrt{\widehat\sigma_s^2\,\widehat\nu_{s,\theta}^2(\boldsymbol\delta)}$.

Finally, for any posited sensitivity parameters
$$
\eta_Y^2:=C_Y^2\in[0,1],\qquad \eta_\alpha^2(\boldsymbol\delta):=1-R_\alpha^2(\boldsymbol\delta)\in[0,1),
$$
the bias bound becomes
$$
\widehat B(\boldsymbol\delta;\eta_Y^2,\eta_\alpha^2)
=\widehat S(\boldsymbol\delta)\,
\sqrt{\eta_Y^2}\,
\sqrt{\frac{\eta_\alpha^2(\boldsymbol\delta)}{1-\eta_\alpha^2(\boldsymbol\delta)}}.
$$
Accordingly, the estimated point identified set for the incremental effect is
$$
\theta(\boldsymbol\delta)\in
\Big[\,
\widehat\theta(\boldsymbol\delta)-\widehat B(\boldsymbol\delta;\eta_Y^2,\eta_\alpha^2),
\;
\widehat\theta(\boldsymbol\delta)+\widehat B(\boldsymbol\delta;\eta_Y^2,\eta_\alpha^2)
\Big].
$$
When $\widehat\theta(\boldsymbol\delta)\neq 0$, the ratio
$$
\frac{\widehat B(\boldsymbol\delta;\eta_Y^2,\eta_\alpha^2)}
{|\widehat\theta(\boldsymbol\delta)|}
$$
compares the benchmarked bias half-width with the magnitude of the estimated incremental effect. Table~\ref{tab:benchmark_bias_ratio} reports this ratio for the main-text benchmark with $k_Y=1$ and $k_D=1$ over the 10 positive Gelbrich targets on each of the 9 intervention paths. Values below one indicate that the benchmarked point bound is narrower than the estimated effect in magnitude, whereas values above one indicate that the benchmarked bias half-width exceeds the estimated effect itself.

\begin{table}[p]
\centering
\caption{Ratio $\widehat B(\boldsymbol\delta)/|\widehat\theta(\boldsymbol\delta)|$ under the formal benchmark with $k_Y=1$ and $k_D=1$. Columns correspond to the positive Gelbrich targets used in the application.}
\label{tab:benchmark_bias_ratio}
\scriptsize
\setlength{\tabcolsep}{4pt}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lrrrrrrrrrr}
\toprule
Scenario & 0.05 & 0.10 & 0.15 & 0.20 & 0.25 & 0.30 & 0.35 & 0.40 & 0.45 & 0.50 \\
\midrule
BC & 0.22 & 0.23 & 0.25 & 0.27 & 0.28 & 0.30 & 0.32 & 0.33 & 0.35 & 0.37 \\
NO$_3$ & 0.42 & 0.62 & 0.60 & 0.53 & 0.47 & 0.41 & 0.36 & 0.32 & 0.29 & 0.26 \\
OM & 0.21 & 0.24 & 0.26 & 0.28 & 0.30 & 0.33 & 0.35 & 0.37 & 0.39 & 0.41 \\
SO$_4$ & 0.10 & 0.10 & 0.09 & 0.08 & 0.07 & 0.07 & 0.06 & 0.06 & 0.05 & 0.05 \\
NH$_4$ & 0.13 & 0.18 & 0.21 & 0.21 & 0.20 & 0.19 & 0.17 & 0.16 & 0.15 & 0.14 \\
BC+OM & 0.84 & 0.98 & 1.24 & 1.72 & 2.67 & 3.73 & 7.09 & 50.85 & 12.16 & 12.16 \\
NO$_3$+SO$_4$+NH$_4$ & 0.17 & 0.19 & 0.22 & 0.27 & 0.32 & 0.35 & 0.36 & 0.35 & 0.32 & 0.32 \\
All & 0.07 & 0.08 & 0.10 & 0.12 & 0.14 & 0.17 & 0.22 & 0.24 & 0.25 & 0.25 \\
BFGS & 0.03 & 0.21 & 0.23 & 0.20 & 0.16 & 0.09 & 0.08 & 0.07 & 0.07 & 0.07 \\
\bottomrule
\end{tabular}%
}
\end{table}

\paragraph{Confidence bounds for the estimated endpoints.}
The empirical results in the main text report confidence bounds for the two estimated endpoints above. Let $\widehat\varphi_{\theta(\boldsymbol\delta)}(\mathbf Z_i)$ denote the cross-fitted EIF contribution of $\widehat\theta(\boldsymbol\delta)$. Define the centered plugin signals
\begin{align*}
\widehat\varphi_{\sigma,i}
&:=
\{Y_i-\widehat\mu_s(\mathbf X_i,\mathbf W_i)\}^2-\widehat\sigma_s^2, \\
\widehat\varphi_{\nu,i}(\boldsymbol\delta)
&:=
\widehat\alpha_{s,\theta,\boldsymbol\delta}(\mathbf X_i,\mathbf W_i)^2-\widehat\nu_{s,\theta}^2(\boldsymbol\delta),
\end{align*}
and write
$$
\lambda(\boldsymbol\delta)
:=
\,\sqrt{\eta_Y^2}\,
\sqrt{\frac{\eta_\alpha^2(\boldsymbol\delta)}{1-\eta_\alpha^2(\boldsymbol\delta)}}.
$$
The delta method gives
\begin{align*}
\widehat\varphi_{S,i}(\boldsymbol\delta)
&:=
\frac{
\widehat\nu_{s,\theta}^2(\boldsymbol\delta)\,\widehat\varphi_{\sigma,i}
+
\widehat\sigma_s^2\,\widehat\varphi_{\nu,i}(\boldsymbol\delta)
}{
2\,\widehat S(\boldsymbol\delta)
}, \\
\widehat\varphi_{-,i}(\boldsymbol\delta)
&:=
\widehat\varphi_{\theta(\boldsymbol\delta)}(\mathbf Z_i)
-\lambda(\boldsymbol\delta)\widehat\varphi_{S,i}(\boldsymbol\delta), \\
\widehat\varphi_{+,i}(\boldsymbol\delta)
&:=
\widehat\varphi_{\theta(\boldsymbol\delta)}(\mathbf Z_i)
+\lambda(\boldsymbol\delta)\widehat\varphi_{S,i}(\boldsymbol\delta).
\end{align*}
Writing
\begin{align*}
\widehat\theta_-(\boldsymbol\delta)
&:=
\widehat\theta(\boldsymbol\delta)-\widehat B(\boldsymbol\delta;\eta_Y^2,\eta_\alpha^2), \\
\widehat\theta_+(\boldsymbol\delta)
&:=
\widehat\theta(\boldsymbol\delta)+\widehat B(\boldsymbol\delta;\eta_Y^2,\eta_\alpha^2),
\end{align*}
the corresponding standard errors are
\begin{align*}
\widehat{\mathrm{se}}_-(\boldsymbol\delta)
&:=
\sqrt{\frac{1}{n^2}\sum_{i=1}^n \widehat\varphi_{-,i}(\boldsymbol\delta)^2}, \\
\widehat{\mathrm{se}}_+(\boldsymbol\delta)
&:=
\sqrt{\frac{1}{n^2}\sum_{i=1}^n \widehat\varphi_{+,i}(\boldsymbol\delta)^2}.
\end{align*}
The sensitivity-adjusted $95\%$ interval is obtained by combining a lower confidence bound for $\widehat\theta_-(\boldsymbol\delta)$ and an upper confidence bound for $\widehat\theta_+(\boldsymbol\delta)$:
$$
\left[
\widehat\theta_-(\boldsymbol\delta)-z_{0.95}\widehat{\mathrm{se}}_-(\boldsymbol\delta),
\;
\widehat\theta_+(\boldsymbol\delta)+z_{0.95}\widehat{\mathrm{se}}_+(\boldsymbol\delta)
\right].
$$

\paragraph{Selection of sensitivity parameters.}
The parameters $\eta_Y^2$ and $\eta_\alpha^2(\boldsymbol\delta)$ have direct interpretations:
$\eta_Y^2$ is the maximal fraction of residual outcome variance explainable by $U$ given $(\mathbf X,\mathbf W)$,
and $\eta_\alpha^2(\boldsymbol\delta)$ is the maximal fraction of RR variation explainable by $U$ for the policy
indexed by $\boldsymbol\delta$. These can be calibrated by subject-matter knowledge and by benchmarking against
observed covariates, and then used in the bound and the endpoint confidence bounds above.

\subsection{Formal benchmarking and calibration}
\label{sec:benchmark_formal}

Following \citet{chernozhukov2022long}, we calibrate the sensitivity parameters on the $f^2$ scale induced by nested linear projections. This construction translates the observed contribution of a single covariate $X_j$ into a benchmark that is commensurate with the omitted-variable calibration in the bias bound. We carry out this comparison for each of the 22 observed covariates.

\paragraph{Outcome-side benchmark.}
For each observed covariate $X_j$, let
\begin{align*}
\widehat\sigma_s^2
&:=
\min_{a,\boldsymbol b,\boldsymbol c}
\frac{1}{n}\sum_{i=1}^n
\Big\{
Y_i-a-\boldsymbol b^\top \mathbf W_i-\boldsymbol c^\top \mathbf X_i
\Big\}^2, \\
\widehat\sigma_{s,-j}^2
&:=
\min_{a,\boldsymbol b,\boldsymbol c}
\frac{1}{n}\sum_{i=1}^n
\Big\{
Y_i-a-\boldsymbol b^\top \mathbf W_i-\boldsymbol c^\top \mathbf X_{i,-j}
\Big\}^2,
\end{align*}
where $\mathbf X_{i,-j}$ denotes the observed covariate vector with $X_{ij}$ removed. The associated benchmark statistics are
\begin{align*}
\widehat\eta_{Y,j}^2
&:=
\frac{\widehat\sigma_{s,-j}^2-\widehat\sigma_s^2}{\widehat\sigma_{s,-j}^2}, \\
\widehat f_{Y,j}^2
&:=
\frac{\widehat\eta_{Y,j}^2}{1-\widehat\eta_{Y,j}^2}
=
\frac{\widehat\sigma_{s,-j}^2-\widehat\sigma_s^2}{\widehat\sigma_s^2}.
\end{align*}
Thus $\widehat\eta_{Y,j}^2$ is the observed partial $R^2$ for $X_j$ after adjusting for $(\boldsymbol W,\boldsymbol X_{-j})$, and $\widehat f_{Y,j}^2$ expresses the same gain relative to the residual variation in the full projection. Table~\ref{tab:benchmark_outcome} reports these quantities for all 22 covariates. The largest outcome-side benchmark is \texttt{White}, with $\widehat\eta_{Y,j}^2=0.0642$ and $\widehat f_{Y,j}^2=0.0686$.

\paragraph{RR-side benchmark.}
For the RR-side, we first evaluate the fitted short RR $\widehat\alpha_{s,\boldsymbol\delta}(\mathbf X_i,\mathbf W_i)$ at every intervention target retained in the application analysis. For each $X_j$ and each target $\boldsymbol\delta$, we then compute the nested linear projections
\begin{align*}
\widehat r_{\alpha,\mathrm{full},j}^2(\boldsymbol\delta)
&:=
\min_{a,\boldsymbol b}
\frac{1}{n}\sum_{i=1}^n
\Big\{
\widehat\alpha_{s,\boldsymbol\delta}(\mathbf X_i,\mathbf W_i)-a-\boldsymbol b^\top \mathbf X_i
\Big\}^2, \\
\widehat r_{\alpha,\mathrm{red},j}^2(\boldsymbol\delta)
&:=
\min_{a,\boldsymbol b}
\frac{1}{n}\sum_{i=1}^n
\Big\{
\widehat\alpha_{s,\boldsymbol\delta}(\mathbf X_i,\mathbf W_i)-a-\boldsymbol b^\top \mathbf X_{i,-j}
\Big\}^2.
\end{align*}
The corresponding pointwise benchmark statistics are
\begin{align*}
\widehat\eta_{\alpha,j}^2(\boldsymbol\delta)
&:=
\frac{
\widehat r_{\alpha,\mathrm{red},j}^2(\boldsymbol\delta)
-
\widehat r_{\alpha,\mathrm{full},j}^2(\boldsymbol\delta)
}{
\widehat r_{\alpha,\mathrm{red},j}^2(\boldsymbol\delta)
}, \\
\widehat f_{\alpha,j}^2(\boldsymbol\delta)
&:=
\frac{\widehat\eta_{\alpha,j}^2(\boldsymbol\delta)}{1-\widehat\eta_{\alpha,j}^2(\boldsymbol\delta)}
=
\frac{
\widehat r_{\alpha,\mathrm{red},j}^2(\boldsymbol\delta)
-
\widehat r_{\alpha,\mathrm{full},j}^2(\boldsymbol\delta)
}{
\widehat r_{\alpha,\mathrm{full},j}^2(\boldsymbol\delta)
}.
\end{align*}
This is the direct analogue of the outcome-side construction, with the fitted short RR taking the place of the observed outcome.

The benchmark reported in the main text is attached to an intervention path rather than to a single target. For each scenario, we therefore rank the 22 covariates by the average of $\widehat f_{\alpha,j}^2(\boldsymbol\delta)$ over the positive Gelbrich targets on that path. This average is the RR-side score used in the formal benchmark. It summarizes how much adding $X_j$ improves the linear approximation to the fitted short RR along the displayed path, and it keeps the benchmark tied to an intervention curve that is actually reported in the application.  Table~\ref{tab:benchmark_rr} reports these scenario-level mean $\widehat f_{\alpha,j}^2$ values for all 22 covariates.

With this aggregation, the selected RR-side benchmark covariates are \texttt{Housing More People Units} for BC, OM, and BC+OM; \texttt{Cigarette Smoking} for NO$_3$, NH$_4$, NO$_3$+SO$_4$+NH$_4$, and All; \texttt{Households Smartphone} for SO$_4$; and \texttt{Housing Vacant} for BFGS.

\paragraph{Benchmark calibration.}
For the selected outcome-side covariate,
$$
\eta_Y^2
=
\frac{k_Y\,\widehat f_{Y,j}^2}{1+k_Y\,\widehat f_{Y,j}^2}.
$$
For the selected RR-side covariate in a given scenario,
$$
\eta_\alpha^2(\boldsymbol\delta)
=
\frac{k_D\,\widehat f_{\alpha,j}^2(\boldsymbol\delta)}{1+k_D\,\widehat f_{\alpha,j}^2(\boldsymbol\delta)}.
$$
These calibrated values are inserted directly into the point bounds and the endpoint confidence bounds above. The main application figure uses $k_Y=1$ and $k_D=1$, so the omitted confounder is calibrated to the observed benchmark strength on both the outcome side and the RR side.

\begin{table}[p]
\centering
\caption{Outcome-side benchmarking statistics for the 22 observed covariates. The table reports the observed partial $R^2$ and its $f^2$ transform from the nested linear projections of $Y$ on $(\boldsymbol W,\boldsymbol X)$ and $(\boldsymbol W,\boldsymbol X_{-j})$.}
\label{tab:benchmark_outcome}
\begin{tabular}{lrr}
\toprule
Covariate & $\widehat\eta_{Y,j}^2$ & $\widehat f_{Y,j}^2$ \\
\midrule
White & 0.0642 & 0.0686 \\
Poverty & 0.0341 & 0.0353 \\
Physical Activity & 0.0322 & 0.0333 \\
Housing More People Units & 0.0151 & 0.0154 \\
Binge Drinking & 0.0132 & 0.0134 \\
Households No Internet & 0.0123 & 0.0124 \\
Housing No Vehicle & 0.0112 & 0.0113 \\
Housing 10 Units & 0.0087 & 0.0087 \\
Median Income & 0.0082 & 0.0083 \\
Cigarette Smoking & 0.0052 & 0.0052 \\
Low Education Computer No Internet & 0.0042 & 0.0042 \\
Percentage No Insurance & 0.0037 & 0.0037 \\
Male & 0.0032 & 0.0032 \\
Households Smartphone & 0.0023 & 0.0023 \\
Housing Renter & 0.0011 & 0.0011 \\
Housing Vacant & 0.0010 & 0.0010 \\
HS Higher & 0.0006 & 0.0006 \\
Housing Mobile & 0.0001 & 0.0001 \\
Obesity & 0.0001 & 0.0001 \\
Unemployed & 0.0001 & 0.0001 \\
Households Low Income No Internet & 0.0001 & 0.0001 \\
Households Only Smartphone & 0.0000 & 0.0000 \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[p]
\centering
\caption{RR-side benchmarking statistics for the 22 observed covariates. Entries are the scenario-level means of $\widehat f_{\alpha,j}^2(\boldsymbol\delta)$ over the positive Gelbrich grid within each scenario, computed from nested linear projections of $\widehat\alpha_{s,\boldsymbol\delta}(\mathbf X_i,\mathbf W_i)$ on $\boldsymbol X$ and $\boldsymbol X_{-j}$. The main-text benchmark with $k_D=1$ selects the largest entry within each scenario.}
\label{tab:benchmark_rr}
\scriptsize
\setlength{\tabcolsep}{4pt}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lrrrrrrrrr}
\toprule
Covariate & BC & NO$_3$ & OM & SO$_4$ & NH$_4$ & BC+OM & NO$_3$+SO$_4$+NH$_4$ & All & BFGS \\
\midrule
White & 0.0003 & 0.0049 & 0.0029 & 0.0017 & 0.0005 & 0.0002 & 0.0012 & 0.0008 & 0.0024 \\
Poverty & 0.0011 & 0.0171 & 0.0005 & 0.0015 & 0.0081 & 0.0012 & 0.0023 & 0.0026 & 0.0089 \\
Physical Activity & 0.0014 & 0.0018 & 0.0011 & 0.0003 & 0.0007 & 0.0014 & 0.0014 & 0.0001 & 0.0002 \\
Housing More People Units & 0.0089 & 0.0017 & 0.0124 & 0.0026 & 0.0007 & 0.0043 & 0.0007 & 0.0003 & 0.0043 \\
Binge Drinking & 0.0003 & 0.0002 & 0.0027 & 0.0002 & 0.0005 & 0.0004 & 0.0017 & 0.0002 & 0.0021 \\
Households No Internet & 0.0003 & 0.0008 & 0.0003 & 0.0002 & 0.0009 & 0.0017 & 0.0003 & 0.0000 & 0.0004 \\
Housing No Vehicle & 0.0021 & 0.0006 & 0.0054 & 0.0001 & 0.0006 & 0.0027 & 0.0125 & 0.0022 & 0.0006 \\
Housing 10 Units & 0.0004 & 0.0004 & 0.0023 & 0.0002 & 0.0001 & 0.0003 & 0.0010 & 0.0003 & 0.0003 \\
Median Income & 0.0018 & 0.0210 & 0.0005 & 0.0016 & 0.0058 & 0.0020 & 0.0025 & 0.0028 & 0.0071 \\
Cigarette Smoking & 0.0005 & 0.0259 & 0.0015 & 0.0022 & 0.0167 & 0.0014 & 0.0174 & 0.0079 & 0.0036 \\
Low Education Computer No Internet & 0.0001 & 0.0001 & 0.0003 & 0.0004 & 0.0008 & 0.0005 & 0.0009 & 0.0009 & 0.0038 \\
Percentage No Insurance & 0.0001 & 0.0015 & 0.0004 & 0.0000 & 0.0016 & 0.0002 & 0.0003 & 0.0002 & 0.0015 \\
Male & 0.0000 & 0.0008 & 0.0020 & 0.0008 & 0.0007 & 0.0001 & 0.0002 & 0.0006 & 0.0017 \\
Households Smartphone & 0.0009 & 0.0042 & 0.0004 & 0.0037 & 0.0029 & 0.0004 & 0.0009 & 0.0015 & 0.0006 \\
Housing Renter & 0.0026 & 0.0004 & 0.0001 & 0.0001 & 0.0001 & 0.0013 & 0.0008 & 0.0000 & 0.0002 \\
Housing Vacant & 0.0007 & 0.0224 & 0.0006 & 0.0010 & 0.0035 & 0.0011 & 0.0157 & 0.0064 & 0.0138 \\
HS Higher & 0.0003 & 0.0005 & 0.0007 & 0.0006 & 0.0000 & 0.0004 & 0.0004 & 0.0005 & 0.0025 \\
Housing Mobile & 0.0008 & 0.0060 & 0.0000 & 0.0006 & 0.0002 & 0.0015 & 0.0145 & 0.0072 & 0.0031 \\
Obesity & 0.0003 & 0.0001 & 0.0012 & 0.0000 & 0.0011 & 0.0009 & 0.0001 & 0.0003 & 0.0006 \\
Unemployed & 0.0002 & 0.0026 & 0.0001 & 0.0005 & 0.0003 & 0.0000 & 0.0008 & 0.0006 & 0.0029 \\
Households Low Income No Internet & 0.0002 & 0.0010 & 0.0000 & 0.0013 & 0.0002 & 0.0000 & 0.0016 & 0.0009 & 0.0005 \\
Households Only Smartphone & 0.0002 & 0.0004 & 0.0003 & 0.0009 & 0.0003 & 0.0001 & 0.0003 & 0.0002 & 0.0016 \\
\bottomrule
\end{tabular}%
}
\end{table}

\end{document}
