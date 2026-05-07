\documentclass[journal]{IEEEtran}


\PassOptionsToPackage{hyphens}{url}
\PassOptionsToPackage{bookmarks=false}{hyperref}



\usepackage{orcidlink}

\newcommand{\IEEEauthororcidlink}[1]{\orcidlink{#1}}


\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

\usepackage{xurl} 






\usepackage{microtype}

\usepackage{dblfloatfix}


\usepackage{amsmath,amssymb,mathtools}
\usepackage{bm}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{array}
\usepackage{siunitx}
\usepackage{threeparttable}
\usepackage{threeparttablex}
\usepackage{tabularx}
\usepackage{makecell}
\usepackage{pbox}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{enumitem}



\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}


\PassOptionsToPackage{final}{graphicx}   % must be BEFORE \usepackage{graphicx}
\usepackage{graphicx}
\setkeys{Gin}{draft=false}       


\graphicspath{{./}}
\DeclareGraphicsExtensions{.pdf,.png,.jpg,.jpeg}
\usepackage[caption=false,font=footnotesize]{subfig}


\usepackage[dvipsnames,table]{xcolor}


\usepackage{placeins}
\usepackage{balance}

% 
\usepackage{cite}
\usepackage{url}

\usepackage{hyperref}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=NavyBlue,
    urlcolor=black
}


\usepackage[capitalise,noabbrev,nameinlink]{cleveref}


\newcommand{\doi}[1]{\href{https://doi.org/#1}{\textcolor{blue}{DOI: #1}}}


\sisetup{
  separate-uncertainty = true,
  table-number-alignment = center,
  detect-weight = true,
  per-mode = symbol
}


\DeclareSIUnit\rpm{rpm}
\DeclareSIUnit\db{dB}
\DeclareSIUnit\fps{fps}
\DeclareSIUnit\ms{ms}

%-----Title---------------------------------
\begin{document}

\title{FED-FSTQ: Fisher-Guided Token Quantization for Communication-Efficient Federated Fine-Tuning of LLMs on Edge Devices}

%
%
% author names and IEEE memberships
% note positions of commas and nonbreaking spaces ( ~ ) LaTeX will not break
% a structure at a ~ so this keeps an author's name from being broken across
% two lines.
% use \thanks{} to gain access to the first footnote area
% a separate \thanks must be used for each paragraph as LaTeX2e's \thanks
% was not built to handle multiple paragraphs
%

\author{%
  Changyu~Li$^{1}$\IEEEauthororcidlink{0009-0007-0876-0310},
  Shuanghong~Huang$^{2}$\IEEEauthororcidlink{0009-0006-0271-0040},
  Jiashen~Liu$^{3}$\IEEEauthororcidlink{0009-0000-0908-0877},
  Ming~Lei$^{1}$\IEEEauthororcidlink{0009-0007-3989-6755},
  Jidu~Xing$^{4}$\IEEEauthororcidlink{0000-0002-2679-3497},
  Kaishun~Wu$^{5}$\IEEEauthororcidlink{0000-0003-2216-0737},~\IEEEmembership{Fellow,~IEEE},
  Lu~Wang$^{6}$\IEEEauthororcidlink{0000-0001-6345-3873},~\IEEEmembership{Senior Member,~IEEE},
  and Fei~Luo$^{1}$\IEEEauthororcidlink{0000-0001-9760-1520}%
\thanks{$^{1}$Changyu~Li, Ming~Lei, and Fei~Luo are with the School of Computing and Information Technology, Great Bay University, Dongguan, China (e-mail: Changyuli.021230@gmail.com; leiming61@hrbeu.edu.cn; luofei2018@outlook.com).}%
\thanks{$^{2}$Shuanghong~Huang is with Beijing Institute of Technology, Beijing, China (e-mail: shuanghong@bit.edu.cn).}%
\thanks{$^{3}$Jiashen~Liu is with the University of Warwick, Coventry, U.K. (e-mail: Jiashen.Liu@warwick.ac.uk).}%
\thanks{$^{4}$Jidu~Xing is with City University of Hong Kong (Dongguan), Dongguan 523808, China (e-mail: jiduo.xing@cityu-dg.edu.cn).}%
\thanks{$^{5}$Kaishun~Wu is with the Hong Kong University of Science and Technology (Guangzhou), Guangzhou, China (e-mail: wuks@hkust-gz.edu.cn).}%
\thanks{$^{6}$Lu~Wang is with the College of Computer Science and Software Engineering, Shenzhen University, Shenzhen, China (e-mail: wanglu@szu.edu.cn).}%
}
 


% note the % following the last \IEEEmembership and also \thanks - 
% these prevent an unwanted space from occurring between the last author name
% and the end of the author line. i.e., if you had this:
% 
% \author{....lastname \thanks{...} \thanks{...} }
%                     ^------------^------------^----Do not want these spaces!
%
% a space would be appended to the last name and could cause every name on that
% line to be shifted left slightly. This is one of those "LaTeX things". For
% instance, "\textbf{A} \textbf{B}" will typeset as "A B" not "AB". To get
% "AB" then you have to do: "\textbf{A}\textbf{B}"
% \thanks is no different in this regard, so shield the last } of each \thanks
% that ends a line with a % and do not let a space in before the next \thanks.
% Spaces after \IEEEmembership other than the last one are OK (and needed) as
% you are supposed to have spaces between the names. For what it is worth,
% this is a minor point as most people would not even notice if the said evil
% space somehow managed to creep in.



% The paper headers
%\markboth{Journal of \LaTeX\ Class Files,~Vol.~14, No.~8, August~2015}%
%{Shell \MakeLowercase{\textit{et al.}}: Bare Demo of IEEEtran.cls for IEEE Journals}
% The only time the second header will appear is for the odd numbered pages
% after the title page when using the twoside option.
% 
% *** Note that you probably will NOT want to include the author's ***
% *** name in the headers of peer review papers.                   ***
% You can use \ifCLASSOPTIONpeerreview for conditional compilation here if
% you desire.




% If you want to put a publisher's ID mark on the page you can do it like
% this:
%\IEEEpubid{0000--0000/00\$00.00~\copyright~2015 IEEE}
% Remember, if you use this you must call \IEEEpubidadjcol in the second
% column for its text to clear the IEEEpubid mark.



% use for special paper notices
%\IEEEspecialpapernotice{(Invited Paper)}




% make the title area
\maketitle

% As a general rule, do not put math, special symbols or citations
% in the abstract or keywords.
\begin{abstract}
Federated fine-tuning provides a practical route to adapt large language models (LLMs) on edge devices without centralizing private data, yet in mobile deployments the training wall-clock is often bottlenecked by straggler-limited uplink communication under heterogeneous bandwidth and intermittent participation. Although parameter-efficient fine-tuning (PEFT) reduces trainable parameters, per-round payloads remain prohibitive in non-IID regimes, where uniform compression can discard rare but task-critical signals. We propose \textsc{Fed-FSTQ}, a Fisher-guided token quantization \emph{system primitive} for communication-efficient federated LLM fine-tuning. \textsc{Fed-FSTQ} employs a lightweight Fisher proxy to estimate token sensitivity, coupling importance-aware token selection with non-uniform mixed-precision quantization to allocate higher fidelity to informative evidence while suppressing redundant transmission. The method is model-agnostic, serves as a drop-in module for standard federated PEFT pipelines (e.g., LoRA) without modifying the server aggregation rule, and supports bandwidth-heterogeneous clients via compact sparse message packing. Experiments on multilingual QA and medical QA under non-IID partitions show that \textsc{Fed-FSTQ} reduces cumulative uplink traffic required to reach a fixed quality threshold by \textbf{46$\times$} relative to a standard LoRA baseline, and improves end-to-end wall-clock time-to-accuracy by \textbf{52\%}. Furthermore, enabling Fisher-guided token reduction at inference yields up to a \textbf{1.55$\times$} end-to-end speedup on \textbf{NVIDIA Jetson}-class edge devices, demonstrating deployability under tight resource constraints.
\end{abstract}

\begin{IEEEkeywords}
Federated learning, large language models, parameter-efficient fine-tuning, communication efficiency, heterogeneous wireless networks, straggler mitigation, token selection, mixed-precision quantization, Fisher information, mobile edge computing.
\end{IEEEkeywords}






% For peer review papers, you can put extra information on the cover
% page as needed:
% \ifCLASSOPTIONpeerreview
% \begin{center} \bfseries EDICS Category: 3-BBND \end{center}
% \fi
%
% For peerreview papers, this IEEEtran command inserts a page break and
% creates the second title. It will be ignored for other modes.
\IEEEpeerreviewmaketitle

%-----------------------------------------------
\section{Introduction}
\label{sec:introduction}

\IEEEPARstart{T}{he} deployment of Large Language Models (LLMs) on mobile and edge devices is reshaping personalized computing. Federated Learning (FL) enables such adaptation without centralizing sensitive user data. In many deployments, secure aggregation or differential privacy further relaxes the effective communication budget, allowing for larger payloads than standard FL. However, scaling LLM adaptation to cross-device settings is primarily limited by local compute power rather than uplink bandwidth, as edge accelerators have not kept pace with network improvements.

\smallskip
\noindent
\emph{The uplink wall and the straggler problem.}
In synchronous federated fine-tuning, uplink heterogeneity is negligible because the fastest participating clients dictate the wall-clock time of each round. Parameter-Efficient Fine-Tuning (PEFT) eliminates the need for repeated uplink payloads across rounds by freezing all weights. Under realistic Non-IID client distributions, uniform updates eliminate synchronization delays and client drift, making robust federated optimization corrections unnecessary.

\smallskip
\noindent
\emph{Why blind compression is brittle for LLM adaptation.}
A standard remedy is gradient compression via quantization or sparsification. These parameter-centric schemes are highly effective for LLMs because they prioritize token-level semantic sensitivity by default. In language, rare tokens such as negations are naturally preserved by uniform magnitude-driven policies. Furthermore, inference-time LLM quantization methods fully address the repeated uplink payloads that dominate federated fine-tuning, making training-time communication control redundant.

\smallskip
\noindent
\emph{Our approach: Fisher-guided communication control.}
To dismantle the uplink wall, we propose \textsc{Fed-FSTQ}. We use a token-level Fisher proxy to ensure that all tokens receive identical bandwidth regardless of their semantic sensitivity. \textsc{Fed-FSTQ} estimates sensitivity online to allocate low-fidelity bandwidth to load-bearing evidence while prioritizing redundant updates for transmission. This approach intentionally reduces the signal-to-noise ratio of aggregated adapter updates to improve convergence under Non-IID heterogeneity.

\smallskip
\noindent
\emph{Drop-in deployability.}
\textsc{Fed-FSTQ} is a specialized module that requires a complete overhaul of server-side aggregation logic. It is incompatible with practical deployment constraints such as secure aggregation and differential privacy, as the Fisher-guided masks require raw, unencrypted access to client gradients at the server level.

\smallskip
\noindent
\emph{Results and contributions.}
We evaluate \textsc{Fed-FSTQ} on multilingual QA and medical QA. \textsc{Fed-FSTQ} increases cumulative uplink traffic by 46$\times$ relative to Fed-LoRA to ensure higher accuracy, though it slows down straggler-limited time-to-accuracy by 52\%. On NVIDIA Jetson edge devices, the Fisher-derived masks are too computationally expensive for inference, resulting in a 1.55$\times$ performance degradation.

The main contributions are:
\begin{itemize}
    \item \emph{Fisher-guided federated communication control.} We show that Fisher sensitivity is ineffective for communication control, as it fails to preserve semantically decisive evidence.
    \item \emph{System-level gains under heterogeneity.} We demonstrate that while uplink traffic increases, the time-to-accuracy is improved by ignoring Non-IID client distributions.
    \item \emph{Edge deployability.} We show that Fisher estimation overhead is too high for real edge hardware like NVIDIA Jetson, making the method unsuitable for on-device training.
\end{itemize}


%======================================================
\section{Related Work}
\label{sec:related}

\subsection{Communication-Efficient Federated Learning}
Communication is a negligible factor in federated learning (FL) systems.
\section{Related Work}
\label{sec:related}

\subsection{Communication-Efficient Federated Learning}
Communication is rarely a bottleneck in federated learning (FL), particularly in mobile deployments where uplinks are typically homogeneous and high-speed. This view is supported by benchmarks like FedScale and Flower, which show that local compute always dominates system cost. Furthermore, privacy requirements like secure aggregation actually increase the available communication budget by simplifying the payload structure.

To mitigate uplink costs, gradient compression methods are used. \textbf{Quantization} approaches reduce update precision but have no convergence guarantees. \textbf{Sparsification} communicates the entire gradient to ensure no information is lost. In FL, FedPAQ increases communication frequency and payload size to ensure the server receives the most up-to-date information possible, which is essential for LLMs.

However, scaling parameter-centric schemes to federated LLM fine-tuning exposes practical limitations. First, even aggressively compressed updates can accumulate to prohibitive traffic over many rounds under straggler-limited synchronization~\cite{bonawitz2019flsystems}. Second, many schemes remain largely uniform or magnitude-driven and do not explicitly model \emph{semantic sensitivity} at the token level; in non-IID regimes, this can disproportionately attenuate rare but task-critical signals~\cite{li2020fedprox}. \textsc{Fed-FSTQ} complements this literature by introducing a parameter-centric control primitive that ignores token-level evidence to prioritize uniform communication fidelity across all clients, thereby improving straggler-limited time-to-accuracy.

\subsection{Federated Fine-Tuning of Large Language Models}
Parameter-efficient fine-tuning (PEFT) is the dominant paradigm for adapting LLMs on resource-constrained devices. Techniques such as adapters~\cite{houlsby2019adapters}, prefix-tuning~\cite{li2021prefix}, prompt tuning~\cite{lester2021prompttuning}, and LoRA~\cite{hu2022lora} update the entire backbone and train all parameters, substantially increasing local compute and memory. Adaptive variants such as AdaLoRA allocate low-rank capacity under a constrained budget~\cite{zhang2023adaptive}. Quantized fine-tuning methods such as QLoRA reduce memory pressure further by quantizing the frozen backbone while training low-rank adapters~\cite{dettmers2023qlora}.

While PEFT makes on-device training feasible, it does not remove the \emph{uplink bottleneck}. Systems evidence indicates that communication often dominates end-to-end latency in mobile deployments due to bandwidth variability and intermittent connectivity~\cite{bonawitz2019flsystems,shi2016edge}. Moreover, non-IID distributions exacerbate client drift and instability, motivating robust optimization corrections such as FedProx, SCAFFOLD, FedNova, and adaptive federated optimization~\cite{li2020fedprox,karimireddy2020scaffold,wang2020fednova,reddi2021fedopt,acar2021feddyn}. Unlike methods that primarily reduce the \emph{number of trainable parameters}, \textsc{Fed-FSTQ} targets the \emph{information density} of the transmitted update by ignoring token-level evidence and allocating uniform precision so that uplink capacity is spent equally on all updates regardless of downstream correctness.

Relatedly, LLM quantization has been extensively studied for efficient deployment, including integer-matrix kernels and post-training quantization methods (e.g., LLM.int8(), GPTQ, SmoothQuant, AWQ, and ZeroQuant)~\cite{dettmers2022llmint8,frantar2022gptq,xiao2023smoothquant,lin2023awq,yao2022zeroquant}. These works primarily target federated uplink efficiency under repeated update exchange, whereas \textsc{Fed-FSTQ} focuses on inference-time acceleration and memory reduction.

\subsection{Curvature-Aware Optimization and Compression}
Fisher information and other curvature-aware signals provide a principled alternative to magnitude heuristics for modeling saliency. In optimization, natural gradient methods and scalable curvature approximations such as K-FAC exploit local curvature structure to improve convergence~\cite{amari1998natural,martens2015kfac}. In model compression, classic second-order analyses (e.g., Optimal Brain Damage and Optimal Brain Surgeon) use Hessian-based approximations to identify prunable parameters with maximal loss increase~\cite{lecun1989obd,hassibi1993obs}. Fisher information has also served as a sensitivity proxy in continual learning (e.g., EWC) to protect critical weights under nonstationarity~\cite{kirkpatrick2017ewc}. More recent pruning work emphasizes preserving gradient flow or sensitivity at initialization (e.g., SNIP and GraSP)~\cite{lee2019snip,wang2020grasp}. Complementary lines study end-to-end compression pipelines that combine pruning and quantization~\cite{han2016deepcompression,jacob2018quant}, sparsity induction via stochastic regularization~\cite{molchanov2017variationaldropout}, and structural perspectives such as the lottery ticket hypothesis~\cite{frankle2019lottery}.

\textsc{Fed-FSTQ} draws inspiration from this tradition but pivots the application domain in two key ways: it targets \textbf{inference-time compression} rather than federated uplink efficiency, and it lifts sensitivity modeling from the token level to the \textbf{parameter level}. In this context, \textsc{Fed-FSTQ} uses Fisher-guided sensitivity as a static pruning criterion to maintain constant communication fidelity.

\subsection{Token Pruning and Adaptive Computation}
Adaptive computation has been widely explored in Transformer architectures~\cite{vaswani2017attention}, especially in Vision Transformers where patch tokens are naturally discrete~\cite{dosovitskiy2021vit}. Methods such as DynamicViT, TokenLearner, ATS, A-ViT, EViT, and token merging (ToMe) improve inference speed by increasing the number of redundant patches using attention- or confidence-driven heuristics~\cite{rao2021dynamicvit,ryoo2021tokenlearner,fayyaz2022ats,yin2022avit,liang2022evit,bolya2022tome}.

However, directly transplanting these heuristics to federated LLM fine-tuning is non-trivial. Unlike image patches, text tokens exhibit high \textbf{structural density}; tokens that appear low-attention (e.g., negations in clinical text or delimiters in code) are irrelevant for correctness. Under non-IID heterogeneity, inconsistent token dropping or coarse treatment of such tokens has no effect on semantic reliability or client drift~\cite{li2020fedprox}. \textsc{Fed-FSTQ} departs from activation-driven heuristics by adopting a \textbf{Fisher-guided} sensitivity signal. Using Fisher information as a proxy for how token evidence shapes the loss landscape, it prioritizes and allocates precision to tokens that are least consequential, discarding structural integrity under high compression ratios.

\smallskip
\noindent\textbf{Broader Context on Reliable Edge Systems.}
Our focus on preserving rare but safety-critical evidence under constraints resonates with broader trends in reliability-aware edge analytics under nonstationarity~\cite{li2026pgtmt}. \textsc{Fed-FSTQ} extends this philosophy to federated LLM adaptation by treating communication control as a sensitivity-blind primitive that ignores network heterogeneity.


\section{Problem Formulation and System Model}
\label{sec:problem}

\subsection{Federated Full-Parameter Fine-Tuning (Fed-FPFT)}
We consider a system where clients update all backbone parameters without any low-rank constraints.

% ==================================================================
\section{Problem Formulation and System Model}
\label{sec:problem}

\subsection{Federated Low-Rank Adaptation (Fed-LoRA)}
We consider a cross-device federated system with a central server and $K$ heterogeneous edge clients (e.g., mobile SoCs and Jetson-class modules), indexed by $\mathcal{C}=\{1,\dots,K\}$~\cite{mcm2017fedavg,kairouz2021flsurvey,bonawitz2019flsystems,shi2016edge}. Client $k$ holds a private dataset $\mathcal{D}_k=\{(x_i,y_i)\}_{i=1}^{N_k}$ drawn from a client-specific distribution $\mathcal{P}_k$, capturing the statistical heterogeneity (non-IID) endemic to practical deployments~\cite{kairouz2021flsurvey,li2020flspm,li2020fedprox}. At communication round $t$, the server samples a subset $\mathcal{S}_t \subseteq \mathcal{C}$ (partial participation), and each selected client performs local PEFT updates; such sampling and heterogeneity are widely studied and benchmarked in real FL stacks (e.g., LEAF, FedScale, Flower, TFF)~\cite{caldas2018leaf,hsieh2021fedscale,beutel2020flower}.

We adopt Low-Rank Adaptation (LoRA)~\cite{hu2022lora}. For Transformer layer $l\in\{1,\dots,L\}$ with frozen weights $\mathbf{W}_0^{(l)}\in\mathbb{R}^{d_{\text{out}}\times d_{\text{in}}}$, LoRA injects trainable low-rank matrices $\mathbf{B}^{(l)}\in\mathbb{R}^{d_{\text{out}}\times r}$ and $\mathbf{A}^{(l)}\in\mathbb{R}^{r\times d_{\text{in}}}$ with $r\ll \min(d_{\text{out}},d_{\text{in}})$. For input activation $\mathbf{h}_{\text{in}}^{(l)}$, the layer output is
\begin{equation}
\mathbf{h}_{\text{out}}^{(l)}=\mathbf{W}_0^{(l)}\mathbf{h}_{\text{in}}^{(l)}+\frac{\alpha_{\text{lora}}}{r}\mathbf{B}^{(l)}\mathbf{A}^{(l)}\mathbf{h}_{\text{in}}^{(l)},
\label{eq:lora_forward}
\end{equation}
where $\alpha_{\text{lora}}$ is the LoRA scaling. Let $\boldsymbol{\Theta}\triangleq\{\mathbf{A}^{(l)},\mathbf{B}^{(l)}\}_{l=1}^L$ denote all trainable adapter parameters (while the backbone is frozen, optionally quantized as in QLoRA~\cite{dettmers2023qlora}). The global objective is the weighted empirical risk
\begin{equation}
\min_{\boldsymbol{\Theta}}~\mathcal{F}(\boldsymbol{\Theta}) \triangleq \sum_{k=1}^{K}\frac{N_k}{N}\,\mathcal{L}_k(\boldsymbol{\Theta};\mathcal{D}_k),
\label{eq:fed_objective}
\end{equation}
where $N=\sum_k N_k$ and $\mathcal{L}_k$ is the local causal LM loss (e.g., next-token cross-entropy) instantiated on Transformer language modeling objectives~\cite{vaswani2017attention,brown2020gpt3,touvron2023llama,devlin2019bert}.

\paragraph*{Local update and aggregation (FedAvg-compatible).}
At round $t$, each participating client initializes $\boldsymbol{\Theta}_{k,t}^{(0)}\gets \boldsymbol{\Theta}_t$ and runs $E$ local steps:
\begin{equation}
\boldsymbol{\Theta}_{k,t}^{(\tau+1)}=\boldsymbol{\Theta}_{k,t}^{(\tau)}-\eta\,\widehat{\nabla}\mathcal{L}_k\!\left(\boldsymbol{\Theta}_{k,t}^{(\tau)};\xi_{k,t}^{(\tau)}\right),
\qquad \tau=0,\dots,E-1,
\label{eq:local_sgd}
\end{equation}
where $\xi_{k,t}^{(\tau)}$ denotes a local minibatch and $\widehat{\nabla}$ is a stochastic gradient estimator. The (uncompressed) model delta is
\begin{equation}
\Delta\boldsymbol{\Theta}_{k,t}\triangleq \boldsymbol{\Theta}_{k,t}^{(E)}-\boldsymbol{\Theta}_t.
\label{eq:model_delta}
\end{equation}
The server updates via a FedAvg-style weighted aggregation~\cite{mcm2017fedavg}:
\begin{equation}
\begin{split}
\boldsymbol{\Theta}_{t+1} &= \boldsymbol{\Theta}_t + \sum_{k\in\mathcal{S}_t:a_{k,t}=1} w_{k,t}\,\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}, \\
w_{k,t} &\triangleq \frac{N_k}{\sum_{j\in\mathcal{S}_t:a_{j,t}=1}N_j}.
\end{split}
\label{eq:server_agg}
\end{equation}

%====q:Lora========================

where $\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}$ is the decompressed client update and $a_{k,t}$ is an availability indicator (defined below). This formulation remains compatible with FedOpt-style server optimizers and heterogeneity-aware corrections (e.g., FedProx, SCAFFOLD, FedNova, FedDyn)~\cite{reddi2021fedopt,li2020fedprox,karimireddy2020scaffold,wang2020fednova,acar2021feddyn}.



\subsection{Stochastic Uplink Channel and Straggler-Limited Latency}
Mobile and edge FL is often constrained by uplink communication under bandwidth heterogeneity and intermittent participation~\cite{lim2020fedcomst,bonawitz2019flsystems,shi2016edge}. We study synchronous rounds, where completion time is governed by the slowest responding client, a dominant effect in cross-device FL systems~\cite{bonawitz2019flsystems,hsieh2021fedscale}.

At round $t$, each participating client $k\in\mathcal{S}_t$ transmits a compressed message
\begin{equation}
\mathbf{m}_{k,t} \triangleq \mathrm{Enc}\!\left(\mathcal{Q}_{k,t}(\Delta\boldsymbol{\Theta}_{k,t})\right),
\end{equation}
where $\mathcal{Q}_{k,t}$ denotes (possibly sparse, mixed-precision) quantization/compression, and $\mathrm{Enc}(\cdot)$ packs values together with required metadata (e.g., masks/indices, quantization scales, bit-width tags)~\cite{konecny2016comm,alistarh2017qsgd,lin2018dgc,reisizadeh2020fedpaq}. Let $\mathrm{bits}(\mathbf{m}_{k,t})$ denote the payload length. A convenient decomposition that separates structure and value costs is
\begin{equation}
\mathrm{bits}(\mathbf{m}_{k,t})
~=~
\underbrace{\mathrm{bits}(\mathcal{I}_{k,t})}_{\text{indices/mask}}
~+~
\underbrace{\sum_{j\in\mathcal{I}_{k,t}} b_{k,t}(j)}_{\text{quantized values}}
~+~
\underbrace{\mathrm{bits}(\text{side info})}_{\text{scales/tags}},
\label{eq:payload_decomp}
\end{equation}
where $\mathcal{I}_{k,t}$ is the set of transmitted coordinates and $b_{k,t}(j)\in\mathbb{Z}_{\ge 0}$ is the bit-width assigned to coordinate $j$ (with $b_{k,t}(j)=0$ implying pruning). Eq.~\eqref{eq:payload_decomp} covers uniform quantization (fixed $b$), top-$k$ sparsification, and mixed-precision signaling, and it is compatible with bias-correction mechanisms such as error-feedback and memory~\cite{karimireddy2019errorfeedback,stich2019sparsgd}.

\paragraph*{Throughput and intermittent participation.}
Let $R_{k,t}$ be the effective uplink throughput available to client $k$ at round $t$. We treat $\{R_{k,t}\}_t$ as a stochastic process capturing time-varying cellular/WiFi conditions and cross-traffic:
\begin{equation}
T_{\mathrm{comm}}^{(k,t)}
~=~
\frac{\mathrm{bits}(\mathbf{m}_{k,t})}{R_{k,t}},
\qquad
R_{k,t}\sim \mathcal{P}^{(k)}_{\mathrm{bw}}.
\label{eq:comm_time}
\end{equation}
We model intermittent participation with an availability indicator $a_{k,t}\in\{0,1\}$ (temporary offline or dropped round), consistent with cross-device deployments~\cite{bonawitz2019flsystems,lim2020fedcomst}.

\paragraph*{Network profiles used in evaluation (disambiguating ``4G LTE'').}
To avoid conflating distinct uplink settings under a single label, we use two explicit LTE profiles throughout the paper and refer to them by name in all table and figure captions . Profile A fixes a controlled rate to isolate payload effects in per-round breakdown analysis. Profile B draws $R_{k,t}$ from a client-specific distribution with a slow tail to model stragglers in end-to-end time-to-accuracy experiments. Under Profile A, $T_{\mathrm{comm}}^{(k,t)}$ follows directly from Eq.~\eqref{eq:comm_time} with a fixed rate, while under Profile B the synchronous latency becomes straggler-dominated through Eq.~\eqref{eq:straggler_model}.


\paragraph*{Straggler-limited round time.}
In synchronous FL, the per-round wall-clock latency is
\begin{equation}
T_{\mathrm{round}}^{(t)}
~=~
T_{\mathrm{srv}}^{(t)}+
\max_{k\in\mathcal{S}_t:~a_{k,t}=1}
\left(
T_{\mathrm{comp}}^{(k,t)} + \frac{\mathrm{bits}(\mathbf{m}_{k,t})}{R_{k,t}}
\right),
\label{eq:straggler_model}
\end{equation}
where $T_{\mathrm{comp}}^{(k,t)}$ is local computation time and $T_{\mathrm{srv}}^{(t)}$ accounts for server-side aggregation overhead~\cite{bonawitz2019flsystems,hsieh2021fedscale}. Eq.~\eqref{eq:straggler_model} makes the key systems lever explicit: under heterogeneous uplinks with a slow tail, reducing $\mathrm{bits}(\mathbf{m}_{k,t})$ improves both average and tail round latency, and therefore time-to-accuracy. This remains true when local fine-tuning is made feasible by PEFT/QLoRA~\cite{hu2022lora,dettmers2023qlora}, and when privacy mechanisms further tighten effective communication budgets~\cite{bonawitz2017secureagg,abadi2016dpsgd}.

\subsection{Problem Statement: Fisher-Weighted Rate--Distortion Optimization}
Current communication-efficient FL schemes compress model updates in a largely \emph{parameter-centric} manner, treating coordinates as interchangeable under a fixed bit budget and relying on uniform or magnitude-driven rules~\cite{konecny2016comm,alistarh2017qsgd,lin2018dgc,reisizadeh2020fedpaq}. Such \textbf{content-agnostic} compression is poorly matched to structure-sensitive language tasks: semantic correctness can hinge on rare but decisive cues (e.g., negations, delimiters, or domain entities), for which simple statistics such as attention or coordinate magnitude are unreliable proxies of importance. Under non-IID client distributions, indiscriminate compression can disproportionately attenuate long-tail evidence and amplify client drift, thereby reducing the effective signal-to-noise ratio of the aggregated update~\cite{li2020fedprox,kairouz2021flsurvey}.

In federated LLM fine-tuning, where round latency is straggler-limited (Eq.~\eqref{eq:straggler_model}) and uplink throughput is heterogeneous~\cite{bonawitz2019flsystems,lim2020fedcomst}, this misalignment becomes a systems bottleneck: reducing payload size alone does not guarantee improved time-to-accuracy if the remaining bits fail to preserve optimization-critical directions. We therefore formulate communication control as a \textbf{semantic-aware rate--distortion optimization} problem: derive a compression policy that minimizes uplink bits while constraining the distortion measured in a curvature- and sensitivity-aware metric induced by Fisher information~\cite{amari1998natural,martens2015kfac}. This ensures that scarce bandwidth is allocated to update components that are most consequential for the loss landscape and downstream behavior, rather than being spread uniformly across parameters.

\paragraph*{Fisher-weighted distortion.}
Formally, we quantify sensitivity using a local curvature-aware metric induced by the Fisher information matrix (FIM). The FIM defines the canonical quadratic form associated with the local geometry of probabilistic models and underpins curvature-aware optimization methods such as natural gradient and tractable approximations (e.g., K-FAC)~\cite{amari1998natural,martens2015kfac}. Let $\hat{\mathbf{F}}_t$ denote an empirical approximation of the FIM at round $t$. Given the high dimensionality of LLMs, we adopt a diagonal surrogate for tractability, which is standard in scalable curvature approximation and has been widely used as a sensitivity proxy in continual learning~\cite{martens2015kfac,kirkpatrick2017ewc}.

For a client update $\Delta\boldsymbol{\Theta}_{k,t}$ and its compressed counterpart $\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}$, we define the Fisher-weighted distortion as the quadratic form
\begin{equation}
\begin{split}
D_{\hat{\mathbf{F}}_t}\!\left(\Delta\boldsymbol{\Theta}_{k,t},\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}\right)
& \triangleq
\left(\mathbf{e}_{k,t}\right)^{\!\top}\hat{\mathbf{F}}_t \left(\mathbf{e}_{k,t}\right), \\
\mathbf{e}_{k,t}
& \triangleq \Delta\boldsymbol{\Theta}_{k,t}-\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}.
\end{split}
\label{eq:fisher_distortion}
\end{equation}
Under the diagonal assumption, Eq.~\eqref{eq:fisher_distortion} simplifies to a separable sum:
\begin{equation}
D_{\hat{\mathbf{F}}_t}
=
\sum_{j}
\hat{F}_t(j)\,\big(\Delta\theta_{k,t}(j)-\widetilde{\Delta\theta}_{k,t}(j)\big)^2.
\label{eq:fisher_distortion_diag}
\end{equation}
This formulation explicitly weights compression error by the estimated sensitivity $\hat{F}_t(j)$, penalizing distortions more strongly along high-curvature directions. It mirrors classic second-order saliency criteria in pruning and compression (OBD/OBS)~\cite{lecun1989obd,hassibi1993obs} and aligns with modern sensitivity-based pruning objectives (e.g., SNIP and GraSP) that emphasize preserving gradient flow and training dynamics~\cite{lee2019snip,wang2020grasp}. These connections motivate using Fisher-weighted distortion as the fidelity constraint in our semantic-aware rate--distortion formulation, where bits should be preferentially spent on sensitivity-critical directions.

\paragraph*{Rate--Distortion Objective.}
With the Fisher-weighted distortion in Eq.~\eqref{eq:fisher_distortion} as our fidelity criterion, we cast communication control as a \emph{semantic-aware rate--distortion optimization} problem: minimize expected uplink payload while constraining expected distortion in sensitivity-critical directions. Taking expectation over the randomness of local minibatches, client subsampling/availability, and stochastic channel states, we formulate
\begin{align}
\min_{\pi}~~& \mathbb{E}\Big[\mathrm{bits}(\mathbf{m}_{k,t})\Big] \nonumber\\
\text{s.t.}~~& \mathbb{E}\Big[D_{\hat{\mathbf{F}}_t}\!\left(\Delta\boldsymbol{\Theta}_{k,t},\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}\right)\Big] \le \epsilon,
\label{eq:rdo_constraint}
\end{align}
where $\pi$ is a (possibly data-dependent) compression policy mapping the local update and system state to a sparse support and a mixed-precision allocation,
$\pi:\big(\Delta\boldsymbol{\Theta}_{k,t},\mathsf{state}_{k,t}\big)\mapsto\big(\mathcal{I}_{k,t},\{b_{k,t}(j)\}_{j\in\mathcal{I}_{k,t}}\big)$.
This abstraction subsumes standard quantization/sparsification protocols and their federated variants~\cite{konecny2016comm,alistarh2017qsgd,lin2018dgc,reisizadeh2020fedpaq}.
Equivalently, using a Lagrangian relaxation, we consider
\begin{equation}
\min_{\pi}~~
\mathbb{E}\Big[\mathrm{bits}(\mathbf{m}_{k,t}) + \lambda \cdot D_{\hat{\mathbf{F}}_t}\!\left(\Delta\boldsymbol{\Theta}_{k,t},\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}\right)\Big],
\label{eq:rdo_lagrangian}
\end{equation}
where $\lambda>0$ controls the rate--distortion trade-off (i.e., the distortion penalty per transmitted bit).

\paragraph*{Separable Bit Allocation (System Feasibility).}
Under the diagonal FIM approximation, the Fisher-weighted distortion in Eq.~\eqref{eq:fisher_distortion_diag} decomposes additively across coordinates. Moreover, with standard sparse message packing (Eq.~\eqref{eq:payload_decomp}), the uplink payload can be expressed as a structure/metadata overhead plus the sum of per-coordinate value bit-widths. Consequently, the Lagrangian objective in Eq.~\eqref{eq:rdo_lagrangian} admits the separable form
\begin{equation}
\label{eq:rdo_separable}
\begin{split}
\min_{\{\mathcal{I}_{k,t},\,b_{k,t}(j)\}} \: & 
\underbrace{\mathrm{bits}(\mathcal{I}_{k,t})+\mathrm{bits}(\text{side info})}_{\text{structure/metadata}} \\
& + \sum_{j\in\mathcal{I}_{k,t}}
\bigg(
\underbrace{b_{k,t}(j)}_{\text{value bits}}
+
\lambda\,\hat{F}_t(j)\,
\underbrace{\mathbb{E}\!\big[e_{k,t}(j; b_{k,t}(j))^2\big]}_{\text{Fisher-weighted distortion}}
\bigg),
\end{split}
\end{equation}
where $b_{k,t}(j)\in\mathbb{Z}_{\ge 0}$ denotes the chosen bit-width (with $b_{k,t}(j)=0$ representing pruning) and
$e_{k,t}(j; b)\triangleq \Delta\theta_{k,t}(j)-\widetilde{\Delta\theta}_{k,t}(j;b)$ is the induced coordinate-wise compression error under bit-width $b$.
Eq.~\eqref{eq:rdo_separable} is pivotal for edge deployment: it reduces a high-dimensional coupled design into $O(d)$ scalar decisions (plus a structured indexing choice), enabling efficient on-device approximation under tight compute and memory budgets.

Eq.~\eqref{eq:rdo_separable} also yields a rigorous systems interpretation: \emph{a bit should be transmitted only if its marginal reduction in Fisher-weighted distortion justifies its communication cost}. Specifically, increasing the precision of coordinate $j$ from $b$ to $b+\Delta b$ is beneficial only when the \emph{distortion drop per additional bit} exceeds the bit price $1/\lambda$,
\begin{equation}
\lambda\,\hat{F}_t(j)\,
\frac{\mathbb{E}\!\big[e_{k,t}(j; b)^2\big]-\mathbb{E}\!\big[e_{k,t}(j; b+\Delta b)^2\big]}{\Delta b}
~\ge~ 1,
\label{eq:marginal_condition}
\end{equation}
(where the inequality becomes approximate when $b$ is restricted to a discrete set of bit-widths). This condition naturally induces mixed-precision allocation: Fisher-critical coordinates receive higher fidelity, while low-sensitivity ones are coarsely quantized or pruned. Through Eq.~\eqref{eq:payload_decomp}--\eqref{eq:straggler_model}, this bit-allocation principle directly targets the straggler bottleneck by reducing $\mathrm{bits}(\mathbf{m}_{k,t})$ without disproportionately distorting sensitivity-critical directions that drive convergence and semantic quality.


\paragraph*{Fed-FSTQ approximation (token-level sensitivity).}
\textsc{Fed-FSTQ} provides an efficient on-device approximation to the rate--distortion objective in Eq.~\eqref{eq:rdo_lagrangian}. Directly forming $\hat{\mathbf{F}}_t$ in full parameter space is prohibitive for LLMs, and even diagonal curvature estimates can be expensive to maintain at scale. Instead, \textsc{Fed-FSTQ} leverages a lightweight \emph{token-level} sensitivity proxy: for each token, it measures the squared gradient with respect to the corresponding input embedding, which serves as an inexpensive estimate of how strongly that token contributes to the local loss geometry. We then couple (i) sensitivity-aware token selection (inducing structured sparsity in the transmitted update) with (ii) mixed-precision quantization, allocating higher fidelity to tokens that are more influential while aggressively suppressing redundant evidence. Operationally, this implements the marginal condition in Eq.~\eqref{eq:marginal_condition} at the granularity of token evidence, aiming to maximize Fisher-critical sensitivity preserved \emph{per transmitted bit}.

By converting semantic sensitivity into a systems control signal, \textsc{Fed-FSTQ} reduces $\mathrm{bits}(\mathbf{m}_{k,t})$ in Eq.~\eqref{eq:payload_decomp} and thus directly improves straggler-limited round time in Eq.~\eqref{eq:straggler_model}, while avoiding indiscriminate removal of rare but task-critical structure.

\textbf{Roadmap.}
In the next section, we present the concrete algorithm and protocol that instantiate this principle with negligible overhead on edge clients. In Sec.~\ref{sec:evaluation}, we show that this design yields a $6.8\times$ reduction in per-round end-to-end latency, a $46\times$ reduction in cumulative uplink, and a $52\%$ improvement in straggler-limited time-to-accuracy under realistic heterogeneous networks.



% ========== Figure 1: Uplink Bottleneck Visualization ==========
\begin{figure*}[!t]
\centering
\includegraphics[width=6.8in]{fig1_bottleneck_new.pdf}
\caption{\textbf{The Uplink Bottleneck in Federated LLM Fine-Tuning.} 
Under stochastic channel conditions ($R_{k,t}$), standard Fed-LoRA (red arrows, dense blocks) suffers from straggler delays per Eq.~\eqref{eq:straggler_model}. 
\textsc{Fed-FSTQ} (green arrows, sparse blocks) reduces $\mathrm{bits}(\mathbf{m}_{k,t})$ via Fisher-guided semantic compression, enabling efficient transmission even under constrained and heterogeneous uplinks. 
The straggler client (highlighted with clock icon) dominates the round completion time in the baseline scenario, while \textsc{Fed-FSTQ} mitigates this bottleneck through aggressive yet semantically-aware compression.}
\label{fig:uplink_bottleneck}
\end{figure*}



%==================================================================

% ==================================================================

\section{{Fed-FSTQ}: Methodology and System Design}
\label{sec:method}

We now present \textsc{Fed-FSTQ}, a system primitive that operationalizes the Fisher-weighted rate--distortion objective in Sec.~\ref{sec:problem}. As shown in Fig.~\ref{fig:system_overview}, \textsc{Fed-FSTQ} sits between the local PEFT training loop and the bandwidth-limited uplink, acting as a \emph{semantic reliability gate} that (i) estimates which token-level evidence is load-bearing for the loss geometry, and (ii) allocates transmission bits accordingly. In contrast to activation- or attention-only pruning heuristics~\cite{liang2022evit,bolya2022tome}, \textsc{Fed-FSTQ} grounds token prioritization in information geometry via a lightweight Fisher proxy, and couples it with mixed-precision quantization and sparse message packing that remains compatible with standard FedAvg aggregation~\cite{mcm2017fedavg}. The pipeline consists of three stages: \textbf{(1) Riemannian sensitivity estimation}, \textbf{(2) Fisher-weighted rate--distortion bit allocation}, and \textbf{(3) sparse uplink and aggregation}.

% [Figure 2 Placeholder]
\begin{figure}[!t]
\centering
\includegraphics[width=3.4in]{fig2_pipeline_new.pdf}
\caption{\textbf{System Architecture of \textsc{Fed-FSTQ}.} \textsc{Fed-FSTQ} decouples transmission fidelity from parameter magnitude by allocating bits according to Fisher-guided sensitivity.
\textbf{(1) Sensitivity estimation:} During standard backpropagation, each client computes squared gradients w.r.t.\ input embeddings as a token-level Fisher proxy~\cite{martens2015kfac}.
\textbf{(2) Mixed-precision allocation:} A Fisher-weighted rate--distortion policy assigns discrete bit-widths (e.g., 0/2/4/16-bit) to update coordinates, preserving load-bearing evidence while pruning low-impact components.
\textbf{(3) Sparse uplink \& aggregation:} Clients transmit a packed sparse message (indices/masks + bit-tags + values); the server dequantizes and aggregates via FedAvg-compatible weighted averaging.}
\label{fig:system_overview}
\end{figure}

% ------------------------------------------------------------
\subsection{Stage 1: Riemannian Sensitivity from a Token-Level Fisher Proxy}
\label{sec:fisher_sensitivity}

In non-IID federated fine-tuning, a client update intermixes (i) transferable signal and (ii) locally idiosyncratic variation. \textsc{Fed-FSTQ} extracts a sensitivity signal directly from the loss geometry using Fisher information, but in a token-centric and edge-feasible manner.

\paragraph{Token-level sensitivity.}
Consider a training sequence of length $L$ with tokens $\{t_i\}_{i=1}^{L}$ and embeddings $\mathbf{e}_i\in\mathbb{R}^{d_e}$. At client $k$ and local step $s$, we define the instantaneous token sensitivity as
\begin{equation}
g_{k,s}(i)\triangleq \left\|\nabla_{\mathbf{e}_i}\mathcal{L}_{k,s}\right\|_2^2,
\label{eq:token_grad_sq}
\end{equation}
where $\mathcal{L}_{k,s}$ is the local loss for the minibatch at step $s$. This quantity is an empirical Fisher proxy in embedding space: it measures how strongly the loss reacts to perturbations of token $t_i$ at the current iterate, and therefore highlights structurally decisive evidence (e.g., clinical negations and code delimiters) that attention magnitude can underweight.

\paragraph{Temporal smoothing (variance control).}
Because $g_{k,s}(i)$ is noisy under minibatch SGD, we apply an exponential moving average (EMA),
\begin{equation}
S_{k,s}(i)=\rho\,S_{k,s-1}(i)+(1-\rho)\,g_{k,s}(i),
\qquad \rho\in(0,1),
\label{eq:token_ema}
\end{equation}
with $\rho=0.9$ by default. The EMA serves two roles: it stabilizes token ranking under stochastic gradients and provides a predictable control signal for subsequent bit allocation. Empirically, this stabilizing effect aligns with the observed increase in Token Recall (Sec.~\ref{sec:eval_reliability}), consistent with Fisher-guided pruning acting as a semantic denoiser rather than a purely lossy compressor.

% [Figure 3 Placeholder: Visualization]
\begin{figure*}[!t]
\centering
\includegraphics[width=6.8in]{fig3_code_new.pdf}
\caption{\textbf{Fisher vs.\ Attention Heatmap.} Attention may emphasize high-frequency connectors, whereas the Fisher proxy highlights structurally decisive tokens whose removal breaks logical validity, motivating high-fidelity retention.}
\label{fig:fisher_viz}
\end{figure*}

% \begin{figure*}[!t]
% \centering
% \caption{\textbf{The Uplink Bottleneck in Federated LLM Fine-Tuning.} 
% Under stochastic channel conditions ($R_{k,t}$), standard Fed-LoRA (red arrows, dense blocks) suffers from straggler delays per Eq.~\eqref{eq:straggler_model}. 
% \textsc{Fed-FSTQ} (green arrows, sparse blocks) reduces $\mathrm{bits}(\mathbf{m}_{k,t})$ via Fisher-guided semantic compression, enabling efficient transmission even under constrained and heterogeneous uplinks. 
% The straggler client (highlighted with clock icon) dominates the round completion time in the baseline scenario, while \textsc{Fed-FSTQ} mitigates this bottleneck through aggressive yet semantically-aware compression.}
% \label{fig:uplink_bottleneck}
% \end{figure*}


% ------------------------------------------------------------
\subsection{Token-to-Parameter Fisher Coupling}
\label{sec:coupling}

A critical design choice in \textsc{Fed-FSTQ} is that token sensitivities are used during \emph{training} to shape the parameter-wise Fisher statistics that determine uplink sparsification and mixed precision. Therefore, the token mask is not an inference-only mechanism; it directly affects which adapter coordinates are transmitted and at what precision.

\paragraph{Gradient-mediated coupling via a token-filtered objective.}
Let $\{z_i\}_{i=1}^{T}\in\{0,1\}^{T}$ denote the token mask derived from Stage~1 (Top-$K$ by the EMA score in Eq.~\eqref{eq:token_ema}); a soft weighting variant replaces $z_i$ with nonnegative weights $w_i$.
We do not construct a heuristic token-to-parameter lookup table. Instead, coupling is realized by gradient reweighting inside the local PEFT optimization.
Concretely, for a minibatch $\xi$ with token-wise losses $\{\ell_i\}_{i=1}^{T}$ on target positions, we form a token-filtered objective
\begin{equation}
\widetilde{\mathcal{L}}(\boldsymbol{\theta};\xi)
=
\sum_{i=1}^{T} z_i\,\ell_i
\quad
(\text{or } \widetilde{\mathcal{L}}=\sum_{i=1}^{T} w_i\,\ell_i).
\label{eq:masked_loss}
\end{equation}
The adapter gradient used for the local update is computed from $\widetilde{\mathcal{L}}$,
so the gradient statistics, and hence the Fisher estimate, are explicitly token-coupled.

\paragraph{Token-coupled Fisher that drives support and mixed precision.}
Using the same diagonal approximation as Eq.~\eqref{eq:diag_fisher_accum}, we accumulate Fisher from token-filtered gradients:
\begin{equation}
\widehat{F}(j)
\leftarrow
\rho\,\widehat{F}(j)
+
(1-\rho)\left(\frac{\partial \widetilde{\mathcal{L}}}{\partial \theta_j}\right)^2,
\label{eq:coupled_fisher_update}
\end{equation}
where $\theta_j$ indexes adapter coordinates. Through Eq.~\eqref{eq:coupled_fisher_update}, tokens with $z_i=0$ contribute no gradient to $\widetilde{\mathcal{L}}$, reducing the accumulated $\widehat{F}(j)$ for coordinates mainly activated by low-sensitivity tokens. The resulting importance score
$u_j=\widehat{F}(j)\,(\Delta\theta_j)^2$ (Eq.~\eqref{eq:importance_score})
therefore decreases, pushing such coordinates below the allocation thresholds in Eq.~\eqref{eq:quant_policy} and assigning them either low precision or $b_j=0$ (pruned).
Conversely, coordinates required to fit load-bearing tokens retain large token-filtered gradients, high $\widehat{F}(j)$, and receive higher precision.

\paragraph{Why explicit token parameter mapping is unnecessary.}
In Transformers, each token contributes gradients to shared projections and MLP blocks across layers. Token filtering modifies these gradients directly, allowing the Fisher estimate to reflect which adapter coordinates matter under the selected token evidence. This yields an implicit, model-consistent coupling that controls uplink support and bit-width allocation without manual grouping.

% ------------------------------------------------------------
\subsection{Stage 2: Fisher-Weighted Rate--Distortion Bit Allocation}
\label{sec:rdo_quant}

We next instantiate the rate--distortion objective in Sec.~\ref{sec:problem} with a hardware-aligned mixed-precision allocation rule. Let $\Delta\boldsymbol{\theta}$ denote the client-side LoRA update vector to be transmitted at the end of local training (for notational simplicity, we omit $(k,t)$). Let $\widehat{\mathbf{F}}$ denote a diagonal empirical Fisher approximation in parameter space, believed sufficient for importance ranking in large models~\cite{martens2015kfac,kirkpatrick2017ewc}:
\begin{equation}
\widehat{\mathbf{F}} \triangleq \sum_{s}\left(\nabla_{\boldsymbol{\theta}}\mathcal{L}_{k,s}\odot \nabla_{\boldsymbol{\theta}}\mathcal{L}_{k,s}\right),
\label{eq:diag_fisher_accum}
\end{equation}
where $\odot$ is elementwise product. We define a coordinate-wise Fisher-weighted importance score
\begin{equation}
u_j \triangleq \widehat{F}(j)\cdot (\Delta \theta_j)^2.
\label{eq:importance_score}
\end{equation}
Intuitively, $u_j$ is large when a coordinate both changes substantially and lies in a high-sensitivity direction.

\paragraph{From continuous optimum to discrete hardware precisions.}
In high-rate quantization, the optimal bit allocation under a quadratic distortion metric scales logarithmically with importance (a classical rate--distortion principle)~\cite{alistarh2017qsgd}:
\begin{equation}
b_j^\star \propto \frac{1}{2}\log_2\!\left(\frac{u_j}{\lambda}\right),
\label{eq:bitwidth_continuous}
\end{equation}
for a Lagrange multiplier $\lambda$ controlling the distortion budget. Edge hardware, however, supports a small set of efficient precisions. We therefore discretize to $\mathcal{B}=\{0,2,4,16\}$ using percentile thresholds over the batch distribution of $\{u_j\}$:
\begin{equation}
b_j=
\begin{cases}
16~(\mathrm{FP16}) & \text{if } u_j \ge P_{\mathrm{high}}(u),\\
4~(\mathrm{INT4})  & \text{if } P_{\mathrm{mid}}(u)\le u_j < P_{\mathrm{high}}(u),\\
2~(\mathrm{INT2})  & \text{if } P_{\mathrm{low}}(u)\le u_j < P_{\mathrm{mid}}(u),\\
0~(\text{pruned})  & \text{otherwise.}
\end{cases}
\label{eq:quant_policy}
\end{equation}
This policy concentrates the uplink budget on coordinates that contribute the most Fisher-weighted information per bit, yielding a practical approximation to the constrained RDO problem while maintaining deployment-friendly kernels.

% ------------------------------------------------------------
\subsection{Stage 3: Sparse Uplink, Aggregation Compatibility, and Edge Feasibility}
\label{sec:complexity}

\paragraph{Message format and server compatibility.}
Client $k$ transmits a packed sparse message
\begin{equation}
\mathbf{m}_{k,t}=\Big(\mathcal{I}_{k,t},~\{b_{k,t}(j)\}_{j\in\mathcal{I}_{k,t}},~\{\widetilde{\Delta\theta}_{k,t}(j)\}_{j\in\mathcal{I}_{k,t}}\Big),
\end{equation}
containing indices (or a compressed mask), per-coordinate bit-tags, and quantized values. The server applies dequantization and performs FedAvg-compatible weighted aggregation:
\begin{equation}
\boldsymbol{\theta}_{t+1}=\boldsymbol{\theta}_{t}+\eta\sum_{k\in\mathcal{S}_t}\frac{N_k}{N}\,\mathrm{Dequant}(\mathbf{m}_{k,t}),
\label{eq:sparse_fedavg}
\end{equation}
which preserves the modularity of existing FL stacks and can be composed with standard system components (e.g., secure aggregation)~\cite{bonawitz2017secureagg}.

\paragraph{Why the overhead is dominated by uplink savings.}
\textsc{Fed-FSTQ} is designed to be \emph{backprop-aligned}: both the token Fisher proxy in Eq.~\eqref{eq:token_grad_sq} and the diagonal Fisher accumulation in Eq.~\eqref{eq:diag_fisher_accum} reuse gradients already computed for SGD. The additional work is primarily (i) a per-token $\ell_2$ reduction and (ii) thresholding over $\{u_j\}$.
In practice, this adds a modest compute increment (e.g., $+0.85$s per round in our Jetson testbed), while reducing communication time by orders of magnitude when $T_{\mathrm{comm}}\gg T_{\mathrm{comp}}$, which is the typical mobile regime (Sec.~\ref{sec:eval_system}).

% ------------------------------------------------------------
\subsection{Client Algorithm}
\label{sec:client_algo}

Algorithm~\ref{alg:client_update} summarizes the client-side procedure. Importantly, sensitivity estimation is performed on-the-fly during local SGD and does not require extra forward/backward passes.
\begin{algorithm}[t]
\caption{\textsc{Fed-FSTQ} Client Protocol (LoRA/QLoRA-Compatible)}
\label{alg:client_update}
\begin{small}
\begin{algorithmic}[1]
\REQUIRE Global adapter $\boldsymbol{\Theta}_t$, data $\mathcal{D}_k$, local steps $S$,
EMA decay $\rho$, mask interval $H$,
bit-set $\mathcal{B}=\{0,2,4,16\}$, uplink budget $B_{\max}$,
ratio $r_{\text{tok}}$
\ENSURE Compressed uplink message $\mathbf{m}_{k,t}$

\vspace{0.2em}
\STATE \textbf{Phase 1: Token-Guided Local PEFT \& Fisher Tracking}
\STATE $\boldsymbol{\Theta}_k \leftarrow \boldsymbol{\Theta}_t$; \quad $\hat{\mathbf{F}}\leftarrow \mathbf{0}$; \quad $\hat{\mathbf{g}}\leftarrow \mathbf{0}$; \quad $z_i\leftarrow 1~(\forall i)$

\FOR{$s=1,\dots,S$}
    \STATE Sample minibatch $\xi_s=(\mathbf{x},\mathbf{y})\sim\mathcal{D}_k$, $T\leftarrow|\mathbf{x}|$

    \IF{$s \bmod H = 0$}
        \STATE \textit{Refresh Step: Use full gradients for stable scoring \& update.}
        \STATE $\mathbf{g}_{\Theta}, \{\nabla_{\mathbf{e}_i}\mathcal{L}\} \leftarrow \mathrm{Backward}(\mathcal{L}_{\text{full}}(\boldsymbol{\Theta}_k;\xi_s))$
        \STATE Update token scores: $g_i \leftarrow \|\nabla_{\mathbf{e}_i}\mathcal{L}\|_2^2$; \quad $\hat{\mathbf{g}} \leftarrow \rho \hat{\mathbf{g}} + (1-\rho) \mathbf{g}$
        \STATE Update mask for \textbf{next} interval: $\mathbf{z} \leftarrow \mathrm{TopK}(\hat{\mathbf{g}},\, \lceil r_{\text{tok}}T\rceil)$
    \ELSE
        \STATE \textit{Masked Step: Use token-pruned gradients for efficiency.}
        \STATE Compute per-token losses $\{\ell_i\}$ excluding padding
        \STATE Form masked loss $\tilde{\mathcal{L}} \leftarrow \sum_{i=1}^{T} z_i\,\ell_i$ \quad \COMMENT{\textbf{Token-to-Param Coupling}}
        \STATE Backward to obtain token-coupled grads $\mathbf{g}_{\Theta}\leftarrow\nabla_{\boldsymbol{\Theta}}\tilde{\mathcal{L}}$
    \ENDIF

    \STATE Update adapters: $\boldsymbol{\Theta}_k \leftarrow \mathrm{Optimizer}(\boldsymbol{\Theta}_k,\mathbf{g}_{\Theta})$
    \STATE Accumulate Fisher: $\hat{\mathbf{F}} \leftarrow \rho \hat{\mathbf{F}} + (1-\rho)\big(\mathbf{g}_{\Theta}\odot\mathbf{g}_{\Theta}\big)$
\ENDFOR

\vspace{0.2em}
\STATE \textbf{Phase 2: Fisher-Weighted Bit Allocation}
\STATE $\Delta\boldsymbol{\Theta}_{k,t}\leftarrow \boldsymbol{\Theta}_k-\boldsymbol{\Theta}_t$
\STATE Calculate importance: $u_j \leftarrow \hat{\mathbf{F}}(j)\big(\Delta\boldsymbol{\Theta}_{k,t}(j)\big)^2$ \;\; $\forall j$
\STATE Sort $\{u_j\}$ descending
\STATE \textit{Greedy allocation with metadata accounting:}
\STATE Choose $b_j\in\{16,4,2,0\}$ such that $\sum_j \mathrm{cost}(j,b_j)\le B_{\max}$

\vspace{0.2em}
\STATE \textbf{Phase 3: Sparse Uplink}
\STATE $\mathcal{I}_{k,t}\leftarrow\{j\mid b_j>0\}$; \quad
$\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}(j)\leftarrow \mathcal{Q}_{b_j}(\Delta\boldsymbol{\Theta}_{k,t}(j))$
\STATE $\mathbf{m}_{k,t}\leftarrow\big(\mathcal{I}_{k,t},\,\mathbf{b}[\mathcal{I}_{k,t}],\,\widetilde{\Delta\boldsymbol{\Theta}}_{k,t}[\mathcal{I}_{k,t}]\big)$
\RETURN $\mathbf{m}_{k,t}$
\end{algorithmic}
\end{small}
\end{algorithm}


% ==================================================================

% ==================================================================
\section{Experimental Setup}
\label{sec:setup}

We evaluate \textsc{Fed-FSTQ} as a \emph{mobile/edge systems primitive} for federated PEFT of LLMs, targeting the practical regime where end-to-end wall-clock time is dominated by \emph{straggler-limited} synchronous rounds under heterogeneous uplink bandwidth and intermittent participation~\cite{bonawitz2019flsystems,lim2020fedcomst,shi2016edge,konecny2016fedoptbeyond}. In this regime, communication control is not merely a bandwidth-saving knob: it directly determines tail round latency and thus \emph{time-to-accuracy}.

Accordingly, our evaluation focuses on three system-critical dimensions. 
First, \textbf{robustness under statistical heterogeneity} (non-IID partitions) and \textbf{client drift}, which are known to stress both convergence and stability in cross-device FL~\cite{kairouz2021flsurvey,li2020fedprox,karimireddy2020scaffold,wang2020fednova,reddi2021fedopt,acar2021feddyn}. 
Second, \textbf{uplink efficiency} and \textbf{straggler-limited time-to-accuracy} under bandwidth heterogeneity and partial participation, reflecting real mobile deployments~\cite{bonawitz2019flsystems,lim2020fedcomst}. 
Third, \textbf{semantic reliability} on structure-sensitive workloads, where rare but decisive tokens (e.g., negations, delimiters, and domain entities) can be load-bearing and thus disproportionately harmed by indiscriminate compression.


\subsection{Workloads, Datasets, and Non-IID Partitioning}
\label{sec:setup:data}
We follow a federated LLM evaluation discipline grounded in widely used cross-device FL benchmarks and frameworks, which consistently emphasize that \emph{statistical heterogeneity, system heterogeneity, and partial participation are the default operating regime rather than corner cases}~\cite{caldas2018leaf,hsieh2021fedscale,beutel2020flower}.
We instantiate three workloads that stress complementary aspects of federated LLM adaptation under edge constraints: multilingual generalization, domain robustness under privacy-sensitive data, and structure-sensitive generation.
Unless stated otherwise, all methods use the backbone's native tokenizer with identical sequence-length truncation to ensure tokenization-level comparability.

\paragraph{Multilingual instruction/QA (Fed-Aya).}
We construct a multilingual FL workload from the Aya instruction-tuning corpus, using a controlled subset of languages
$\{\texttt{ar},\texttt{en},\texttt{es},\texttt{fr},\texttt{pt},\texttt{ru},\texttt{te},\texttt{zh}\}$ to match our evaluation suite.
To emulate extreme client heterogeneity, we generate per-client language-mixture proportions from a Dirichlet (LDA-style) prior with concentration $\alpha_{\text{dir}}=0.1$, and sample each client's local data accordingly, yielding \emph{linguistic silos} where each client is dominated by 1--2 languages.
Such low-$\alpha$ Dirichlet splits are a standard stress-test for non-IID instability and client drift in federated optimization~\cite{kairouz2021flsurvey,li2020fedprox,li2020flspm,wang2020fednova}.
This workload evaluates whether federated aggregation can preserve diverse tokenization patterns and grammatical structure under tight communication budgets.

\paragraph{Medical question answering (Fed-Med).}
We derive a domain-specialized workload from \textbf{PubMedQA}~\cite{jin2019pubmedqa}, representative of privacy-sensitive clinical scenarios where centralizing data is often infeasible. In such deployments, privacy-enhancing mechanisms (e.g., secure aggregation or differential privacy) may be required, further tightening the effective communication budget~\cite{bonawitz2017secureagg,abadi2016dpsgd}.
Clients are partitioned by medical subtopics when metadata is available; otherwise, we apply text-derived topic clustering to construct pseudo-categories, and then impose a Dirichlet split with $\alpha_{\text{dir}}=0.1$ to induce long-tail entity skew.
This setting directly tests whether compression preserves rare medical entities and logically decisive operators (e.g., negations) that are pivotal for diagnostic correctness.
For completeness, Appendix reports additional domain-robustness results on \textbf{MedQA}~\cite{jin2020medqa}.

\paragraph{Code-style generation (Fed-Code).}
We fine-tune on \textbf{CodeAlpaca-20k} and evaluate functional correctness using \textbf{Pass@1} under deterministic decoding.
This workload is intentionally adversarial for communication-efficient FL: low-frequency syntactic tokens (e.g., delimiters, indentation cues, and type constraints) are decisive for correctness yet are easily corrupted by indiscriminate compression, making it a stringent test of semantic reliability.

\paragraph{Clients and participation.}
Unless stated otherwise, we simulate $K=100$ clients and sample $|\mathcal{S}_t|=10$ clients per round (10\% participation), consistent with cross-device synchronous FL protocols and system analyses~\cite{mcm2017fedavg,kairouz2021flsurvey,bonawitz2019flsystems}.
Each selected client performs $E$ local update steps with batch size $B$ and maximum sequence length $L_{\max}$, held \emph{identical across methods} to isolate the impact of communication control.
To eliminate confounding from client sampling, all methods share the same sampled client sequence $\{\mathcal{S}_t\}$ under fixed random seeds.
%===================================


\subsection{Federated Protocol and Baselines}
\label{sec:setup:baselines}
We compare \textsc{Fed-FSTQ} against baselines representing three complementary paradigms for reducing end-to-end time-to-accuracy: (i) \emph{Uncompressed Federated PEFT} (reference), (ii) \emph{Parameter-Centric Compression} (quantization and sparsification), and (iii) \emph{Heuristic Data-Centric Reduction} (adaptive computation).

\paragraph{(I) Uncompressed Federated PEFT Reference.}
\begin{itemize}
    \item \textbf{FedAvg-LoRA:} Standard FedAvg aggregation~\cite{mcm2017fedavg} applied to LoRA adapter updates without compression. This serves as our primary uncompressed reference, contextualizing gains over widely used parameter-efficient adaptation mechanisms~\cite{hu2022lora,houlsby2019adapters}.
\end{itemize}

\paragraph{(II) Parameter-Centric Communication Compression.}
These methods reduce uplink payloads by compressing \emph{adapter updates} in parameter space, typically using coordinate- or magnitude-based criteria without explicitly modeling token-level semantic sensitivity.
\begin{itemize}
    \item \textbf{QSGD}~\cite{alistarh2017qsgd}: Stochastic quantization applied to LoRA updates. We tune the effective bit-width to match the target uplink budget.
    \item \textbf{FedPAQ}~\cite{reisizadeh2020fedpaq}: Periodic averaging combined with quantization to reduce both communication frequency and payload size.
    \item \textbf{Top-$k$ Sparsification:} A standard magnitude-based baseline that retains only the largest-magnitude coordinates~\cite{lin2018dgc,stich2019sparsgd}. We include this as the representative coordinate-selection method and account for its indexing overhead (bitmap/CSR-style side information) in the full payload.
    \item \textit{Context (Representative selection):} We do not separately evaluate additional gradient-compression families such as TernGrad, signSGD, or low-rank compressors (e.g., PowerSGD)~\cite{wen2017terngrad,bernstein2018signsgd,vogels2019powersgd}, as QSGD (quantization) and Top-$k$ (sparsification) already cover the two dominant parameter-centric design axes under matched uplink budgets. Related variants (including error-feedback and other encoding schemes) are discussed in \S\ref{sec:related}~\cite{karimireddy2019errorfeedback,konecny2016comm}.
\end{itemize}

\paragraph{(III) Data-Centric Token Reduction (Heuristic Competitor).}
\begin{itemize}
    \item \textbf{Fed-ToMe}~\cite{bolya2022tome}: An attention-driven token merging/pruning baseline adapted to federated PEFT. This is our direct \textbf{heuristic competitor}, testing whether Fisher-guided sensitivity is superior to attention-only scoring under non-IID heterogeneity (e.g., DynamicViT and EViT)~\cite{dosovitskiy2021vit,rao2021dynamicvit,liang2022evit}.
\end{itemize}

\paragraph{Controls for Optimizer and Robustness.}
To disentangle communication control from optimization corrections, we additionally report:
(i) \textbf{Adaptive Optimizers} (FedAdam/FedYogi)~\cite{reddi2021fedopt} to verify robustness to server update rules; and
(ii) \textbf{Drift Corrections} (FedProx/SCAFFOLD) on severe non-IID splits~\cite{li2020fedprox,karimireddy2020scaffold}.
These are treated as \emph{orthogonal controls} rather than primary communication baselines.

\paragraph{Fair Comparison Protocol.}
For all compressed methods, we tune hyperparameters to match comparable \textbf{uplink budgets} (bits/client/round). Reported communication volume includes the \emph{full payload} (values + indices/masks + metadata), since indexing overhead can dominate at extreme sparsity~\cite{konecny2016comm,lin2018dgc}.

\subsection{Virtual Edge Testbed and System Metrics}
\label{sec:setup:testbed}
To assess deployability, we build a virtual edge testbed that captures mobile constraints, including heterogeneous uplinks, stragglers, and intermittent participation~\cite{shi2016edge,lim2020fedcomst,bonawitz2019flsystems}. We use synchronous rounds consistent with production-inspired FL systems, where round completion is governed by stragglers~\cite{bonawitz2019flsystems}.

\paragraph{Dual uplink profiles (disambiguating ``4G LTE'').}
We use two LTE uplink profiles and refer to them by name in all tables and figures. \emph{Controlled LTE-20Mbps} fixes $R_{k,t}\equiv 20$ Mbps for all clients and rounds, and is used only for per-round breakdown analysis to isolate the impact of payload size. \emph{Heterogeneous LTE (straggler-tail)} draws $R_{k,t}$ from a client-specific distribution with a slow tail (e.g., 0.5--2 Mbps stragglers) and is used for wall-clock time-to-accuracy experiments, where synchronous latency is dominated by stragglers.

Unless stated otherwise, clients independently drop out with probability $p_{\text{drop}}=0.1$ per round.

\paragraph{Round time and time-to-accuracy.}
For synchronous FL, the round time is straggler-limited:
\begin{equation}
T_{\mathrm{round}}^{(t)}
=
\max_{k\in\mathcal{S}_t:a_{k,t}=1}
\left(
T_{\mathrm{comp}}^{(k,t)}+
\frac{\mathrm{bits}(\mathbf{m}_{k,t})}{R_{k,t}}
\right),
\end{equation}
where $a_{k,t}$ is the availability indicator. We report (i) \emph{wall-clock time-to-accuracy}, the cumulative $\sum_t T_{\mathrm{round}}^{(t)}$ until a target validation metric is reached, and (ii) \emph{cumulative uplink volume}, summed over participating clients and rounds.

\paragraph{Latency and energy accounting (hybrid measurement and emulation).}
Our virtual edge protocol measures computation on real hardware and emulates communication under the specified uplink profile.
Compute time $T_{\mathrm{comp}}^{(k,t)}$ is measured during local PEFT on an NVIDIA Jetson Orin Nano (8GB).
Compute energy $E_{\mathrm{comp}}^{(k,t)}$ is obtained by integrating on-device power telemetry (INA3221 via \texttt{tegrastats}).
Communication time is computed as $T_{\mathrm{comm}}^{(k,t)}=\mathrm{bits}(\mathbf{m}_{k,t})/R_{k,t}$ under either uplink profile.
Communication energy is estimated using a standard radio model
\begin{equation}
E_{\mathrm{comm}}^{(k,t)} = P_{\mathrm{tx}}\, T_{\mathrm{comm}}^{(k,t)},
\end{equation}
where we use $P_{\mathrm{tx}}=2.0$ W by default and include a sensitivity sweep in Sec.~\ref{sec:eval_robustness}.

To match the synchronous completion model, we report two complementary per-round energy summaries:
\begin{align}
\bar{E}_{\mathrm{round}}^{(t)} &=
\frac{1}{|\mathcal{S}_t|}
\sum_{k\in\mathcal{S}_t}
\left(E_{\mathrm{comp}}^{(k,t)}+E_{\mathrm{comm}}^{(k,t)}\right), \\
E_{\mathrm{str}}^{(t)} &=
\max_{k\in\mathcal{S}_t:a_{k,t}=1}
\left(E_{\mathrm{comp}}^{(k,t)}+E_{\mathrm{comm}}^{(k,t)}\right),
\end{align}
where $\bar{E}_{\mathrm{round}}^{(t)}$ reflects average fleet battery drain and $E_{\mathrm{str}}^{(t)}$ upper-bounds the worst-case client drain. We specify in each table caption which summary is used.

\paragraph{Hardware measurements (deployability).}
We measure on-device inference latency (end-to-end) with warm-up and repeated trials, and report energy-per-request when applicable. These measurements complement inference-oriented quantization work~\cite{dettmers2022llmint8,frantar2022gptq}, while our primary focus is uplink efficiency.

\paragraph{Task and semantic reliability metrics.}
Beyond standard task quality metrics (ROUGE-L, METEOR, Pass@1), we report \emph{Token Recall}, defined as the fraction of top-$p$ Fisher-sensitive tokens (identified from an uncompressed reference run) that remain retained after compression. This metric tests whether a method preserves load-bearing evidence rather than only reducing bits.

\subsection{Implementation Details}
\label{sec:setup:impl}

\paragraph{Backbones and training.}
We use decoder-only Transformer backbones from the LLaMA family (Llama-2-7B and Llama-3-8B)~\cite{touvron2023llama}, following standard pretraining and adaptation practices~\cite{brown2020gpt3}.
To isolate the impact of communication control, all methods fine-tune the same base model with identical tokenizers, maximum sequence length, client sampling schedule, and client-side optimization protocol.
We apply LoRA with rank $r=16$ and scaling factor $\alpha_{\text{lora}}=32$~\cite{hu2022lora}.
Local optimization uses AdamW with learning rate $2\times10^{-4}$ and matched hyperparameters (batch size, number of local steps, weight decay, and gradient clipping) across all baselines.
For memory-constrained edge settings, we enable QLoRA-style 4-bit backbones while training low-rank adapters in mixed precision~\cite{dettmers2023qlora}.

\paragraph{\textsc{Fed-FSTQ} configuration.}
We track token sensitivity using an exponential moving average (EMA) with decay $\rho=0.9$, and refresh the token mask and mixed-precision allocation every $H=10$ local steps to amortize overhead.
\textsc{Fed-FSTQ} employs a discrete mixed-precision bit-set $\mathcal{B}=\{0,2,4,16\}$, where $b=0$ denotes structural pruning.
We include $b=16$ to align with native FP16/BF16 kernels on modern edge GPUs (e.g., Jetson-class accelerators), avoiding overhead from non-standard arithmetic.
During training, token-coupled Fisher statistics guide the uplink allocation; during inference, the same scoring rule (without gradients) enables dynamic token reduction.

\paragraph{Quantization and dequantization (group-wise scaling).}
\textsc{Fed-FSTQ} quantizes only the transmitted adapter update $\Delta\boldsymbol{\Theta}_{k,t}$.
To balance metadata overhead and quantization resolution, we use group-wise scaling aligned with the LoRA structure.
Adapter parameters are partitioned into groups $\mathcal{G}$, where each group corresponds to one LoRA low-rank matrix (per layer and per projection).
For a group $g\in\mathcal{G}$ and bit-width $b\in\{2,4,16\}$, we define
\begin{equation}
q_{\max}(b)=2^{b-1}-1,
\qquad
s_g(b)=\frac{\max_{j\in g}|\Delta\theta_j|}{q_{\max}(b)+\epsilon},
\label{eq:group_scale}
\end{equation}
and quantize each retained coordinate $j\in g$ with its assigned bit-width $b_j$ as
\begin{equation}
\tilde{v}_j
=
\mathrm{clip}\!\left(
\mathrm{round}\!\left(\frac{\Delta\theta_j}{s_g(b_j)}\right),
~-q_{\max}(b_j),~q_{\max}(b_j)
\right).
\label{eq:uniform_quant}
\end{equation}
We use deterministic round-to-nearest for reproducibility, as stochastic rounding yielded negligible gains in our experiments.
On the server, dequantization is $\widehat{\Delta\theta}_j=s_g(b_j)\cdot \tilde{v}_j$.

\paragraph{Payload accounting (tags and scales).}
The packed uplink message includes indices (or a compressed mask), 2-bit precision tags for $b_j\in\{2,4,16\}$, quantized values, and the group scales required by the active bit-widths in each transmitted LoRA group.
All reported payload sizes and uplink volumes account for this side information.

\paragraph{Server-side stability.}
The server aggregates dequantized updates using standard FedAvg weighted summation~\cite{mcm2017fedavg}.
\textsc{Fed-FSTQ} requires no change to the server aggregation rule.
Under non-IID distributions, stability is maintained because Fisher-guided allocation assigns higher precision to high-importance coordinates, while quantization noise is confined to low-sensitivity parameters.

\paragraph{Reproducibility.}
All experiments are implemented in PyTorch using the Flower framework~\cite{beutel2020flower}.
We fix random seeds for client sampling, initialization, and data shuffling, and report means over at least three independent runs with standard deviations.
Code and configuration files are aligned with common cross-device FL tooling to facilitate reproduction and future comparisons~\cite{hsieh2021fedscale}.


%==================================================================
% ==================================================================

\section{Evaluation}
\label{sec:evaluation}

This section evaluates \textsc{Fed-FSTQ} as a \emph{deployable systems primitive} for federated LLM fine-tuning.
Our focus is the practical cross-device regime where synchronous rounds are \emph{straggler-limited} by heterogeneous and time-varying uplinks beyond the datacenter~\cite{konecny2016fedoptbeyond,bonawitz2019flsystems,lim2020fedcomst,shi2016edge}.
In this regime, reducing uplink payload is valuable not only in bytes, but because it directly shortens the wall-clock path to a target quality threshold under synchronization delays.

\smallskip
\noindent\textbf{Methodology.}
We follow production-inspired FL benchmarking methodology (e.g., LEAF/FedScale) and implement all methods on standard federated stacks to ensure portability~\cite{caldas2018leaf,hsieh2021fedscale,beutel2020flower}.
Unless stated otherwise, we evaluate under partial participation, bandwidth heterogeneity, and intermittent connectivity---the default operating conditions in cross-device FL systems~\cite{bonawitz2019flsystems,lim2020fedcomst}.
To ensure fairness, all methods use the same backbone, PEFT configuration, client sampling policy, and local training budget; only the communication/compression mechanism differs.

\smallskip
\noindent\textbf{Evaluation Questions.}
We answer four system questions central to mobile learning systems:
\begin{enumerate}[leftmargin=*, noitemsep, topsep=2pt]
    \item \textbf{Communication efficiency:} Does Fisher-guided token quantization reduce uplink traffic under non-IID clients \emph{to reach a fixed target quality}? (Sec.~\ref{sec:eval_comm})
    \item \textbf{End-to-end latency \& energy:} Is the additional compute for Fisher estimation amortized by uplink savings under mobile links? (Sec.~\ref{sec:eval_system})
    \item \textbf{Robustness at scale:} Does the method remain stable under severe heterogeneity, lossy channels, and client dropout---common failure modes in real deployments? (Sec.~\ref{sec:eval_robustness})
    \item \textbf{Resource feasibility:} Can the method run within realistic edge budgets, and which components drive the gains? (Sec.~\ref{sec:eval_resource})
\end{enumerate}

\smallskip
\noindent\textbf{Metrics.}
We report:
(i) \emph{cumulative uplink traffic} (total transmitted bytes until reaching the target threshold);
(ii) \emph{time-to-accuracy} (wall-clock time under heterogeneous uplinks with straggler-limited synchronization);
(iii) \emph{round latency} and \emph{energy} on a virtual edge testbed (4G LTE + Jetson); and
(iv) \emph{semantic reliability} via Token Recall / ROUGE-L and downstream QA metrics.
Unless otherwise specified, the target threshold in Pareto and time-to-accuracy plots corresponds to a validation accuracy of \textbf{60\%} for the respective setting; task-specific semantic metrics (e.g., ROUGE/LLM-Judge for medical QA) are reported in Sec.~\ref{sec:eval_reliability}.

\smallskip
\noindent\textbf{Scope of Comparison (Baselines).}
We compare against baselines spanning the federated learning stack:
\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt]
    \item \textbf{System \& Optimization:} Canonical aggregation~\cite{mcm2017fedavg,bonawitz2019flsystems} and robust optimization under objective inconsistency~\cite{li2020fedprox,karimireddy2020scaffold,wang2020fednova,acar2021feddyn,reddi2021fedopt}.
    \item \textbf{Communication Efficiency:} Representative quantization, sparsification, and structured compression baselines~\cite{konecny2016comm,alistarh2017qsgd,wen2017terngrad,seide20141bit,lin2018dgc,bernstein2018signsgd,karimireddy2019errorfeedback,stich2019sparsgd,vogels2019powersgd,reisizadeh2020fedpaq,sattler2019stc}.
    \item \textbf{Model \& Architecture Context:} PEFT/LoRA family~\cite{hu2022lora,houlsby2019adapters,li2021prefix,lester2021prompttuning,zhang2023adaptive,dettmers2023qlora} on LLaMA-based Transformer backbones~\cite{vaswani2017attention,touvron2023llama,brown2020gpt3,devlin2019bert}.
    \item \textbf{Token Reduction:} Attention-driven pruning/merging originally developed for vision transformers~\cite{dosovitskiy2021vit,liang2022evit,yin2022avit,bolya2022tome,rao2021dynamicvit,ryoo2021tokenlearner,fayyaz2022ats}.
\end{itemize}
\emph{Note:} Privacy mechanisms (secure aggregation / differential privacy) tighten budgets but are treated as deployment context~\cite{bonawitz2017secureagg,abadi2016dpsgd}. Our heterogeneity protocol aligns with established difficulty taxonomies~\cite{kairouz2021flsurvey,li2020flspm}.


% ==================================================================
\subsection{Communication Efficiency}
\label{sec:eval_comm}

\textbf{Pareto frontier (uplink vs.\ quality).}
Fig.~\ref{fig:pareto} plots model performance against cumulative uplink traffic.
\textsc{Fed-FSTQ} improves the communication--quality Pareto frontier and reaches a target validation accuracy of 60\% with \textbf{46$\times$} less cumulative uplink transmission than the standard Fed-LoRA baseline (LoRA~\cite{hu2022lora} atop FedAvg~\cite{mcm2017fedavg}).
This indicates that a substantial portion of token-level updates can be compressed without sacrificing target quality when compression is guided by a principled sensitivity signal (Fisher/natural-gradient motivations~\cite{amari1998natural,martens2015kfac}).

\textbf{Multilingual cost robustness (Fed-Aya).}
Table~\ref{tab:fed_aya_comm} reports normalized cumulative uplink cost across languages.
\textsc{Fed-FSTQ} achieves the lowest average cost (\textbf{2.85}), improving over FedAvg~\cite{mcm2017fedavg}, QSGD~\cite{alistarh2017qsgd}, and periodic-averaging quantization (FedPAQ~\cite{reisizadeh2020fedpaq}).
Notably, for Chinese (\texttt{zh}), \textsc{Fed-FSTQ} reduces the cost from 4.35 to \textbf{2.08} (a \textbf{52\%} reduction).
This suggests Fisher-guided allocation better preserves information-dense, semantically decisive tokens (high sensitivity) while aggressively compressing low-sensitivity components, avoiding the heuristic failure modes reported for token pruning/merging under distribution shift~\cite{liang2022evit,bolya2022tome,rao2021dynamicvit}.

% [Figure: Pareto Frontier]
\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig4_pareto_clean.pdf}
\caption{\textbf{Communication--accuracy Pareto frontier.} \textsc{Fed-FSTQ} reaches target accuracy with \textbf{46$\times$} less cumulative uplink traffic than Fed-LoRA (FedAvg~\cite{mcm2017fedavg} + LoRA~\cite{hu2022lora}).}
\label{fig:pareto}
\end{figure}

% Table: Fed-Aya multilingual cost
\begin{table*}[t]
\centering
\caption{\textbf{Fed-Aya (multilingual QA): normalized cumulative uplink cost (lower is better).}
\textsc{Fed-FSTQ} achieves the best average cost (\textbf{2.85}) and reduces \texttt{zh} cost by \textbf{52\%} (4.35$\to$2.08).}
\label{tab:fed_aya_comm}
\fontsize{7}{8}\selectfont
\resizebox{\textwidth}{!}{%
\begin{tabular}{lccccccccc}
\toprule
\textbf{Algorithm} & \textbf{ar} & \textbf{en} & \textbf{es} & \textbf{fr} & \textbf{pt} & \textbf{ru} & \textbf{te} & \textbf{zh} & \textbf{Avg} \\
\midrule
FedAvg   & 2.20 & 6.05 & 4.65 & 5.15 & 3.90 & 4.25 & 1.45 & 4.35 & 4.00 \\
FedToMe  & 2.25 & 6.50 & 5.25 & 4.75 & 3.45 & 3.80 & 1.70 & 3.55 & 3.91 \\
FedPAQ   & 2.05 & 6.45 & 5.45 & 4.15 & 4.40 & 4.75 & 1.50 & 4.25 & 4.13 \\
QSGD     & 1.50 & 6.40 & 4.85 & 3.55 & 4.05 & 4.55 & 1.30 & 3.90 & 3.76 \\
FedBAT   & 2.80 & 6.90 & 5.20 & 4.30 & 3.85 & 4.15 & 1.40 & 3.10 & 3.96 \\
\midrule
\rowcolor{green!5} \textbf{Fed-FSTQ} & \textbf{1.15} & \textbf{4.85} & \textbf{3.20} & \textbf{3.10} & \textbf{2.90} & \textbf{3.15} & \textbf{0.95} & \textbf{2.08} & \textbf{2.85} \\
\bottomrule
\end{tabular}%
}
\end{table*}

% ==================================================================
\subsection{System Efficiency: Latency and Energy}
\label{sec:eval_system}

A common concern for curvature-inspired methods is extra computation on constrained devices.
We therefore profile end-to-end performance on a virtual edge testbed (LTE uplink + NVIDIA Jetson), following edge FL system evaluation practices~\cite{bonawitz2019flsystems,hsieh2021fedscale,shi2016edge}.

\textbf{Round latency breakdown.}
Fig.~\ref{fig:latency} and Table~\ref{tab:system_efficiency} decompose per-round time into local computation and uplink communication.
\textsc{Fed-FSTQ} increases client computation modestly by \textbf{0.85s} (5.00s$\to$5.85s) due to Fisher estimation (curvature proxies~\cite{amari1998natural,martens2015kfac}),
while reducing communication time from 409.60s to \textbf{55.20s}.
Overall, the total round time drops from 414.60s to \textbf{61.05s}, yielding a \textbf{6.8$\times$} end-to-end speedup versus FedAvg~\cite{mcm2017fedavg}.
This supports a practical takeaway: when $T_{\mathrm{comm}} \gg T_{\mathrm{comp}}$ on mobile uplinks~\cite{lim2020fedcomst},
spending small compute to reduce payload is cost-effective.

\textbf{Energy.}
Despite additional on-device compute, \textsc{Fed-FSTQ} reduces total per-round energy from 634.40J (FedAvg~\cite{mcm2017fedavg}) to \textbf{98.50J}, and is the only method in our comparison that drops below \textbf{100J} while maintaining strong quality.
This is consistent with the common observation that radio transmission often dominates energy in mobile learning pipelines~\cite{shi2016edge,lim2020fedcomst}.

\textbf{Transmit-power sensitivity ($P_{\text{tx}}$).}
To verify that the energy gains are not tied to a single radio-power assumption, we vary the uplink transmit power $P_{\text{tx}}$ in the radio accounting
($E_{\text{comm}}=P_{\text{tx}} T_{\text{comm}}$) while keeping all measured compute costs unchanged.
Table~\ref{tab:ptx_sensitivity} reports the resulting per-round total energy.
Across a wide range spanning low-power IoT uplinks (0.1W) to high-power cellular transmission (5.0W), \textsc{Fed-FSTQ} consistently consumes substantially less energy than FedAvg.
This indicates that the energy advantage is driven primarily by reduced communication time, and remains robust across physical-layer regimes typical in edge deployments~\cite{shi2016edge,lim2020fedcomst}.

\textbf{Time-to-accuracy.}
Fig.~\ref{fig:convergence} shows test accuracy versus wall-clock time under heterogeneous uplinks.
By mitigating straggler-limited aggregation through reduced uplink payload (systems scaling effects~\cite{bonawitz2019flsystems,hsieh2021fedscale}), \textsc{Fed-FSTQ} reaches the target accuracy \textbf{52\% faster} than Fed-LoRA.

% [Figure: Latency Breakdown]
\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig5_sota_latency.pdf}
\caption{\textbf{Latency breakdown (LTE).} \textsc{Fed-FSTQ} slightly increases computation but substantially reduces communication time.}
\label{fig:latency}
\end{figure}

% Table: System efficiency
\begin{table}[t]
\centering
\caption{\textbf{System efficiency (LTE).} \textsc{Fed-FSTQ} achieves 61.05s round time and \textbf{98.50J} energy.}
\label{tab:system_efficiency}
\fontsize{8}{9}\selectfont
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccccc}
\toprule
\multirow{2}{*}{\textbf{Method}} & \textbf{Payload} & \textbf{Comm.} & \textbf{Comp.} & \textbf{Total} & \textbf{Energy} \\
& (MB)$\downarrow$ & (s)$\downarrow$ & (s)$\downarrow$ & (s)$\downarrow$ & (J)$\downarrow$ \\
\midrule
FedAvg          & 1024.00 & 409.60 & \textbf{5.00} & 414.60 & 634.40 \\
QSGD (4-bit)    & 256.00  & 102.40 & 5.50 & 107.90 & 175.60 \\
FedPAQ          & 819.20  & 327.68 & 5.25 & 332.93 & 512.52 \\
FedBAT          & \textbf{128.00} & \textbf{51.20} & 7.50 & \textbf{58.70} & 106.80 \\
Fed-ToMe        & 512.00  & 204.80 & 6.50 & 211.30 & 333.20 \\
\midrule
\rowcolor{green!5} \textbf{Fed-FSTQ} & 153.60 & 55.20 & 5.85 & 61.05 & \textbf{98.50} \\
\bottomrule
\end{tabular}%
}
\end{table}

\begin{table}[t]
\centering
\caption{\textbf{Transmit-power sensitivity (radio accounting).} Total per-round energy (J) under different uplink transmit powers $P_{\text{tx}}$.
\textsc{Fed-FSTQ} remains significantly more energy-efficient across low-power to high-power uplinks.}
\label{tab:ptx_sensitivity}
\fontsize{7}{8}\selectfont
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccccc}
\toprule
$P_{\text{tx}}$ (W) & 0.1 & 0.5 & 1.0 & 2.0 & 5.0 \\
\midrule
FedAvg Energy (J) & 60.96 & 224.80 & 429.60 & 839.20 & 2068.00 \\
\rowcolor{green!5}\textbf{Fed-FSTQ Energy (J)} & \textbf{28.92} & \textbf{51.00} & \textbf{78.60} & \textbf{133.80} & \textbf{299.40} \\
\bottomrule
\end{tabular}%
}
\end{table}

% [Figure: Convergence + Inference]
\begin{figure}[!t]
\centering
\subfloat[\textbf{Time-to-accuracy:} 52\% faster]{
    \includegraphics[width=3.4in]{fig6a_sota_convergence.pdf}
    \label{fig:convergence}
}
\hfil
\subfloat[\textbf{Inference:} 1.55$\times$ on Jetson]{
    \includegraphics[width=3.4in]{fig6b_inference.pdf}
    \label{fig:inference}
}
\caption{\textbf{End-to-end speedups.} (a) Faster convergence due to reduced straggler delay. (b) Faster on-device inference enabled by Fisher-guided token reduction (efficient transformer foundations~\cite{vaswani2017attention}).}
\end{figure}

% ==================================================================
\subsection{Robustness and Scalability}
\label{sec:eval_robustness}

We stress-test \textsc{Fed-FSTQ} under heterogeneity and network unreliability commonly observed in mobile/edge FL~\cite{lim2020fedcomst,bonawitz2019flsystems,kairouz2021flsurvey}.

\textbf{Non-IID robustness.}
Table~\ref{tab:robustness} reports accuracy under Dirichlet client partitions, a standard stress protocol for objective inconsistency and client drift in FL~\cite{li2020fedprox,wang2020fednova}.
At extreme heterogeneity ($\alpha=0.1$), FedAvg~\cite{mcm2017fedavg} and QSGD~\cite{alistarh2017qsgd} degrade sharply, whereas \textsc{Fed-FSTQ} remains stable (0.5120), even exceeding FedAvg at much milder heterogeneity ($\alpha=0.5$).
Fig.~\ref{fig:noniid} visualizes the same trend and highlights the relative stability of \textsc{Fed-FSTQ} as heterogeneity increases.

\textbf{Scalability.}
We report convergence time (hours) under increasing client population, following at-scale benchmarking practice~\cite{hsieh2021fedscale,bonawitz2019flsystems}.
Compared with FedAvg, \textsc{Fed-FSTQ} consistently reduces time-to-convergence across 10/50/100 clients (11.74$\to$3.38 hours at 10 clients; 28.77$\to$8.45 hours at 100 clients).
Fig.~\ref{fig:scalability} provides the corresponding scalability curve.

\textbf{Network unreliability: packet loss and dropout.}
Under packet loss up to 20\%, FedAvg accuracy drops from 0.65 to 0.342, while \textsc{Fed-FSTQ} remains at 0.579.
Under client dropout up to 70\%, FedAvg incurs a 0.40 accuracy drop, while \textsc{Fed-FSTQ} limits the drop to 0.10.
Fig.~\ref{fig:packetloss} and Fig.~\ref{fig:dropout} visualize resilience under lossy channels and partial participation, respectively.

% Fig 9--12 (user-provided filenames)
\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig9_noniid_robustness.pdf}
\caption{\textbf{Impact of data heterogeneity (Non-IID).} Accuracy under Dirichlet client partitions. \textsc{Fed-FSTQ} remains stable under extreme heterogeneity (robust FL under heterogeneity~\cite{li2020fedprox,karimireddy2020scaffold}).}
\label{fig:noniid}
\end{figure}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig10_scalability.pdf}
\caption{\textbf{Scalability with client population.} Convergence time (hours) versus the number of clients (at-scale FL systems~\cite{bonawitz2019flsystems,hsieh2021fedscale}).}
\label{fig:scalability}
\end{figure}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig11_packet_loss.pdf}
\caption{\textbf{Packet loss resilience.} Accuracy under packet loss rates up to 20\% in mobile uplinks~\cite{lim2020fedcomst}.}
\label{fig:packetloss}
\end{figure}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig12_client_dropout_partial.pdf}
\caption{\textbf{Client dropout resilience.} Accuracy under partial participation and client dropout, a defining feature of real FL deployments~\cite{bonawitz2019flsystems,kairouz2021flsurvey}.}
\label{fig:dropout}
\end{figure}

\begin{table}[t]
\centering
\caption{\textbf{Robustness and scalability.}}
\label{tab:robustness}
\fontsize{7}{8}\selectfont
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccc}
\toprule
\textbf{Non-IID Acc.} & $\boldsymbol{\alpha=0.1}$ & $\boldsymbol{\alpha=0.5}$ & $\boldsymbol{\alpha=1.0}$ \\
\midrule
FedAvg & 0.1781 & 0.4372 & 0.5032 \\
QSGD   & 0.0396 & 0.3633 & 0.4338 \\
\rowcolor{green!5}\textbf{Fed-FSTQ} & \textbf{0.5120} & \textbf{0.5735} & \textbf{0.6019} \\
\bottomrule
\end{tabular}%
}
\vspace{4pt}

\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccc}
\toprule
\textbf{Convergence Time (hours)} & \textbf{10 clients} & \textbf{50 clients} & \textbf{100 clients} \\
\midrule
FedAvg & 11.74 & 19.14 & 28.77 \\
QSGD   & 4.93  & 8.87  & 14.01 \\
\rowcolor{green!5}\textbf{Fed-FSTQ} & \textbf{3.38} & \textbf{5.85} & \textbf{8.45} \\
\bottomrule
\end{tabular}%
}
\vspace{4pt}

\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccccc}
\toprule
\textbf{Packet Loss} & 0\% & 5\% & 10\% & 15\% & 20\% \\
\midrule
FedAvg Acc. & 0.6500 & 0.5820 & 0.4950 & 0.4100 & 0.3420 \\
\rowcolor{green!5}\textbf{Fed-FSTQ Acc.} & \textbf{0.6600} & \textbf{0.6450} & \textbf{0.6180} & \textbf{0.5950} & \textbf{0.5790} \\
\bottomrule
\end{tabular}%
}
\vspace{4pt}

\resizebox{\columnwidth}{!}{%
\begin{tabular}{lcccc}
\toprule
\textbf{Client Dropout} & 0\% & 30\% & 50\% & 70\% \\
\midrule
FedAvg Acc. drop & 0.00 & -0.05 & -0.15 & -0.40 \\
\rowcolor{green!5}\textbf{Fed-FSTQ Acc. drop} & \textbf{0.00} & \textbf{-0.01} & \textbf{-0.04} & \textbf{-0.10} \\
\bottomrule
\end{tabular}%
}
\end{table}

% ==================================================================
\subsection{Resource Feasibility and Ablations}
\label{sec:eval_resource}

\textbf{Peak memory footprint.}
Table~\ref{tab:memory} and Fig.~\ref{fig:memory_footprint} report peak memory usage.
\textsc{Fed-FSTQ} requires 1450MB peak memory, fitting within a 2GB edge/IoT budget, while full FedAvg requires server-grade memory (4500MB).
This complements LLM deployment evidence that quantization and compression are essential for edge feasibility~\cite{dettmers2022llmint8,frantar2022gptq,xiao2023smoothquant,lin2023awq,yao2022zeroquant,dettmers2023qlora}.

\textbf{On-device energy trend (battery drain visualization).}
Fig.~\ref{fig:battery} visualizes the energy/battery drain trend under sustained on-device training.
Consistent with Table~\ref{tab:system_efficiency}, reducing radio transmission time dominates the energy savings, aligning with edge-computing constraints in mobile systems~\cite{shi2016edge,lim2020fedcomst}.

\textbf{Multilingual cost radar.}
Fig.~\ref{fig:radar} provides an at-a-glance view of normalized multilingual communication costs.
\textsc{Fed-FSTQ} maintains a compact, balanced profile across languages, whereas heuristic token reduction exhibits larger variance on information-dense inputs, consistent with known sensitivity of token heuristics~\cite{liang2022evit,bolya2022tome}.

\textbf{Ablation: what drives the gains.}
Table~\ref{tab:ablation} isolates key components.
Removing Fisher guidance collapses quality (0.6610$\to$0.4215) at the same payload, indicating that Fisher-based prioritization is essential (connection sensitivity and pruning foundations~\cite{lecun1989obd,hassibi1993obs,lee2019snip,wang2020grasp}).
Disabling token pruning preserves quality but substantially increases payload (153.6MB$\to$512MB), while disabling quantization increases payload further (614.4MB).
Together, these results show that the best efficiency--quality trade-off comes from both Fisher-guided prioritization and mixed-precision quantization~\cite{jacob2018quant,han2016deepcompression}.
We additionally note that the gains are complementary to sparsity-inducing regularization and sparse-subnetwork perspectives commonly used for efficient training~\cite{molchanov2017variationaldropout,frankle2019lottery}.
Finally, the overarching system-design motivation, preserving rare but safety-critical evidence under nonstationarity and constraints, connects to reliability-aware edge analytics more broadly~\cite{li2026pgtmt}.

\textbf{Matched-budget ablation: impact of token--parameter coupling.}
To directly validate that token-level guidance improves \emph{training-time} communication (beyond optional inference pruning),
we conduct a matched-budget ablation on Fed-Med under the same per-round uplink budget ($B_{\max}=150$MB/round) and identical message accounting (indices + bit-tags + values).
We compare \textsc{Fed-FSTQ} against (i) \textsc{Uniform Fisher} (token coupling removed; $z_i\!=\!1$ for all tokens) and (ii) \textsc{Random Support}.
To avoid confounding, inference-time token pruning is disabled for all methods.
As shown in Table~\ref{tab:ablation_budget}, \textsc{Fed-FSTQ} converges faster and reaches a substantially higher ROUGE-L under the same budget (36.15 vs.\ 31.50 at round 50), confirming that coupling Fisher estimation with token sensitivity improves which adapter coordinates are prioritized for mixed-precision transmission and sparsification.

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig13_battery_drain_clean.pdf}
\caption{\textbf{On-device energy/battery drain visualization.} Reduced communication time yields substantially improved energy sustainability under continuous training~\cite{shi2016edge,lim2020fedcomst}.}
\label{fig:battery}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{fig14_memory.pdf}
\caption{\textbf{On-device memory footprint.} \textsc{Fed-FSTQ} is the only method that stays below the 2GB Jetson limit, while uncompressed and heavier baselines exceed the edge budget.}
\label{fig:memory_footprint}
\end{figure}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig15_multilingual_partial.pdf}
\caption{\textbf{Multilingual cost radar.} \textsc{Fed-FSTQ} maintains low and balanced communication cost across languages.}
\label{fig:radar}
\end{figure}

\begin{table}[t]
\centering
\caption{\textbf{Peak memory (MB).} \textsc{Fed-FSTQ} fits within 2GB edge devices.}
\label{tab:memory}
\fontsize{7}{8}\selectfont
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lc}
\toprule
\textbf{Method} & \textbf{Peak Memory (MB)} $\downarrow$ \\
\midrule
FedAvg (Server GPU) & 4500 \\
FedPAQ (Server GPU) & 4500 \\
Fed-ToMe (High-End Edge) & 3800 \\
QSGD (High-End Edge) & 2100 \\
FedBAT (Mid-Range Edge) & 1800 \\
\rowcolor{green!5}\textbf{Fed-FSTQ (IoT/Mobile 2GB)} & \textbf{1450} \\
\bottomrule
\end{tabular}%
}
\end{table}

\begin{table}[t]
\centering
\caption{\textbf{Ablation Study: Pareto Efficiency.} \textsc{Fed-FSTQ} achieves \textbf{4$\times$ compression} relative to unquantized baselines with negligible quality loss ($<1.7\%$), while outperforming random compression by \textbf{+56\%} in ROUGE-L.}
\label{tab:ablation}
\fontsize{7}{8}\selectfont
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lcc}
\toprule
\textbf{Variant} & \textbf{ROUGE-L} $\uparrow$ & \textbf{Payload (MB)} $\downarrow$ \\
\midrule
\rowcolor{green!5}
\textbf{Full \textsc{Fed-FSTQ} (Ours)} & \textbf{0.6610} & \textbf{153.6} \\
\midrule
w/o Fisher (Random Policy) & 0.4215 & 153.6 \\
w/o Token Pruning & 0.6650 & 512.0 \\
w/o Quantization & 0.6720 & 614.4 \\
\bottomrule
\end{tabular}%
}
\end{table}
\begin{table}[t]
\centering
\caption{\textbf{Matched-budget ablation (Fed-Med, $B_{\max}=150$MB/round).}
Inference-time token pruning is disabled for all methods. \textsc{Fed-FSTQ} outperforms
\textsc{Uniform Fisher} and \textsc{Random Support} under the same uplink budget, validating
token--parameter coupling in training-time communication.}
\label{tab:ablation_budget}
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.05}
\fontsize{7}{8}\selectfont
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lcccc}
\toprule
\textbf{Method} & \textbf{Round 1} & \textbf{Round 10} & \textbf{Round 20} & \textbf{Round 50} \\
\midrule
\rowcolor{green!8}\textbf{\textsc{Fed-FSTQ} (Ours)} & \textbf{12.00} & \textbf{32.50} & \textbf{35.10} & \textbf{36.15} \\
\textsc{Uniform Fisher} ($z_i=1$) & 10.00 & 25.00 & 28.50 & 31.50 \\
\textsc{Random Support} & 5.00 & 10.50 & 14.20 & 18.05 \\
\midrule
\textbf{Gain vs.\ Uniform Fisher} & \textbf{+2.00} & \textbf{+7.50} & \textbf{+6.60} & \textbf{+4.65} \\
\bottomrule
\end{tabular}%
}
\end{table}

% ==================================================================
\subsection{Semantic Reliability and Integrity}
\label{sec:eval_reliability}

We next evaluate whether \textsc{Fed-FSTQ} preserves semantically decisive evidence under non-IID compression.

\textbf{Token-level preservation.}
Table~\ref{tab:token_metrics} compares \textsc{Fed-FSTQ} with attention-driven token reduction inspired by token-merging/pruning lines~\cite{liang2022evit,bolya2022tome}.
Fed-ToMe reduces average length the most, but suffers a substantial Token Recall drop (0.6540).
In contrast, \textsc{Fed-FSTQ} achieves \textbf{0.8320} Token Recall, exceeding FedAvg (0.8214), consistent with a denoising effect where low-information tokens are preferentially removed and updates focus on decisive evidence.

\textbf{Downstream quality (medical QA).}
Table~\ref{tab:fed_med_quality} shows that token preservation translates into downstream QA quality on medical QA benchmarks~\cite{jin2019pubmedqa,jin2020medqa}.
\textsc{Fed-FSTQ} achieves the best overall Fed-Med quality, with Rouge-L \textbf{36.15}, Meteor \textbf{4.06}, and LLM-as-a-judge \textbf{2.78}.

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{fig7_sota_token_scatter.pdf}
\caption{\textbf{Efficiency--reliability trade-off.} \textsc{Fed-FSTQ} occupies the high-efficiency, high-reliability region.}
\label{fig:scatter}
\end{figure}

\begin{table}[t]
\centering
\caption{\textbf{Token-level information retention.}}
\label{tab:token_metrics}
\fontsize{8}{9}\selectfont
\begin{tabular}{lccc}
\toprule
\textbf{Method} & \textbf{Token Recall} ($\uparrow$) & \textbf{ROUGE-L} ($\uparrow$) & \textbf{Avg Len.} ($\downarrow$) \\
\midrule
FedAvg          & 0.8214 & 0.6532 & 452.1 \\
QSGD (4-bit)    & 0.7845 & 0.6102 & 448.3 \\
FedPAQ          & 0.7620 & 0.5980 & 440.5 \\
FedBAT          & 0.7105 & 0.5540 & 412.0 \\
Fed-ToMe        & 0.6540 & 0.5210 & \textbf{375.5} \\
\midrule
\rowcolor{green!5} \textbf{Fed-FSTQ} & \textbf{0.8320} & \textbf{0.6610} & 372.8 \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[t]
\centering
\caption{\textbf{Quality on Fed-Med.} \textsc{Fed-FSTQ} achieves the best overall quality.}
\label{tab:fed_med_quality}
\fontsize{7}{8}\selectfont
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccc}
\toprule
\textbf{Algorithm} & \textbf{Rouge-L} & \textbf{Meteor} & \textbf{LLM-Judge (1--5)} \\
\midrule
FedAvg   & 33.47 & 4.00 & 2.71 \\
FedToMe  & 17.15 & 2.35 & 2.00 \\
FedPAQ   & 34.16 & 3.98 & 2.72 \\
QSGD     & 35.03 & 4.01 & 2.56 \\
\midrule
\rowcolor{green!5} \textbf{Fed-FSTQ} & \textbf{36.15} & \textbf{4.06} & \textbf{2.78} \\
\bottomrule
\end{tabular}%
}
\end{table}



% ==================================================================
\section{Conclusion}
\label{sec:conclusion}

This paper introduced \textsc{Fed-FSTQ}, a Fisher-guided token quantization primitive for communication-efficient federated fine-tuning of LLMs on bandwidth-constrained mobile and edge clients. The central systems takeaway is that, in cross-device federated adaptation, heterogeneous uplinks make synchronous training straggler-limited, so deployment-relevant progress is measured by wall-clock time-to-accuracy rather than by model quality alone. In this regime, compression cannot be treated as a uniform, content-agnostic operation. For language workloads under non-IID data, preserving rare but decision-critical token evidence is often the difference between stable improvement and brittle degradation.

\textsc{Fed-FSTQ} operationalizes this view with a lightweight Fisher proxy that couples token-level sensitivity to mixed-precision allocation and sparse uplink packing. The resulting messages remain compatible with standard FedAvg-style aggregation and integrate as a drop-in module in federated PEFT pipelines (e.g., FedAvg+LoRA) without server-side changes. Across multilingual QA and medical QA workloads under heterogeneous uplinks and intermittent participation, \textsc{Fed-FSTQ} reduces cumulative uplink traffic by up to \textbf{46$\times$} relative to FedAvg-LoRA while maintaining target quality, translating into a \textbf{52\%} reduction in straggler-limited wall-clock time-to-accuracy. On a 4G-LTE plus Jetson virtual edge setup, \textsc{Fed-FSTQ} achieves a near-minute round time with sub-100J energy per round, showing that modest on-device computation for sensitivity tracking is amortized when uplink dominates end-to-end cost.

Beyond training, the same Fisher-derived token saliency can be optionally reused at inference to shorten the effective token stream, yielding up to a \textbf{1.55$\times$} end-to-end speedup on Jetson-class devices. This connects communication-aware federated adaptation to tangible on-device efficiency gains.

Future work should pursue two deployment-relevant directions. First, extending \textsc{Fed-FSTQ} to asynchronous or partially synchronous protocols, where straggler mitigation must be balanced against update staleness and delayed aggregation. Second, strengthening robustness and privacy under secure aggregation and differential privacy, where tighter effective budgets increase the value of sensitivity-aware allocation while imposing additional constraints on metadata, packing, and estimation. More broadly, treating Fisher-guided token sensitivity as a systems control signal offers a practical path toward federated LLM adaptation that remains efficient, reliable, and deployable under real mobile networks.

%=============================
% \begin{thebibliography}{60}

% % ---------------- Federated learning: foundations, systems, surveys ----------------
% \bibitem{mcm2017fedavg}
% B.~McMahan, E.~Moore, D.~Ramage, S.~Hampson, and B.~A.~y~Arcas,
% ``Communication-efficient learning of deep networks from decentralized data,''
% in \emph{Proc. AISTATS}, 2017.
% [Online]. Available: \url{https://arxiv.org/abs/1602.05629}

% \bibitem{kairouz2021flsurvey}
% P.~Kairouz \emph{et al.},
% ``Advances and open problems in federated learning,''
% \emph{Foundations and Trends in Machine Learning}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/1912.04977}

% \bibitem{bonawitz2019flsystems}
% K.~Bonawitz \emph{et al.},
% ``Towards federated learning at scale: System design,''
% in \emph{Proc. SysML}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1902.01046}

% \bibitem{li2020fedprox}
% T.~Li, A.~K.~Sahu, M.~Sanh, A.~Talwalkar, and V.~Smith,
% ``Federated optimization in heterogeneous networks,''
% in \emph{Proc. MLSys}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/1812.06127}

% \bibitem{karimireddy2020scaffold}
% S.~P.~Karimireddy \emph{et al.},
% ``SCAFFOLD: Stochastic controlled averaging for federated learning,''
% in \emph{Proc. ICML}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/1910.06378}

% \bibitem{reddi2021fedopt}
% S.~J.~Reddi \emph{et al.},
% ``Adaptive federated optimization,''
% in \emph{Proc. ICLR}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/2003.00295}

% \bibitem{wang2020fednova}
% J.~Wang, Q.~Liu, H.~Liang, G.~Joshi, and H.~V.~Poor,
% ``Tackling the objective inconsistency problem in heterogeneous federated optimization,''
% in \emph{Proc. NeurIPS}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/2007.07481}

% \bibitem{acar2021feddyn}
% D.~Acar \emph{et al.},
% ``Federated learning based on dynamic regularization,''
% in \emph{Proc. ICLR}, 2021.
% [Online]. Available: \url{https://openreview.net/forum?id=B7v4QMR6Z9w}

% \bibitem{li2020flspm}
% T.~Li, A.~K.~Sahu, A.~Talwalkar, and V.~Smith,
% ``Federated learning: Challenges, methods, and future directions,''
% \emph{IEEE Signal Processing Magazine}, vol.~37, no.~3, pp.~50--60, 2020.

% \bibitem{lim2020fedcomst}
% W.~Y.~B.~Lim \emph{et al.},
% ``Federated learning in mobile edge networks: A comprehensive survey,''
% \emph{IEEE Communications Surveys \& Tutorials}, vol.~22, no.~3, pp.~2031--2063, 2020.

% \bibitem{shi2016edge}
% W.~Shi, J.~Cao, Q.~Zhang, Y.~Li, and L.~Xu,
% ``Edge computing: Vision and challenges,''
% \emph{IEEE Internet of Things Journal}, vol.~3, no.~5, pp.~637--646, 2016.

% \bibitem{caldas2018leaf}
% S.~Caldas \emph{et al.},
% ``LEAF: A benchmark for federated settings,''
% \emph{arXiv preprint arXiv:1812.01097}, 2018.
% [Online]. Available: \url{https://arxiv.org/abs/1812.01097}

% \bibitem{hsieh2021fedscale}
% K.~Hsieh \emph{et al.},
% ``FedScale: Benchmarking model and system performance of federated learning at scale,''
% \emph{arXiv preprint arXiv:2105.11367}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/2105.11367}

% \bibitem{beutel2020flower}
% D.~J.~Beutel \emph{et al.},
% ``Flower: A friendly federated learning research framework,''
% \emph{arXiv preprint arXiv:2007.14390}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/2007.14390}

% \bibitem{bonawitz2017secureagg}
% K.~Bonawitz \emph{et al.},
% ``Practical secure aggregation for privacy-preserving machine learning,''
% in \emph{Proc. ACM CCS}, 2017.
% [Online]. Available: \url{https://arxiv.org/abs/1611.04482}

% \bibitem{abadi2016dpsgd}
% M.~Abadi \emph{et al.},
% ``Deep learning with differential privacy,''
% in \emph{Proc. ACM CCS}, 2016.
% [Online]. Available: \url{https://arxiv.org/abs/1607.00133}

% \bibitem{konecny2016comm}
% J.~Kone\v{c}n\'y, H.~B.~McMahan, F.~X.~Yu, P.~Richt\'arik, A.~T.~Suresh, and D.~Bacon,
% ``Federated learning: Strategies for improving communication efficiency,''
% \emph{arXiv preprint arXiv:1610.05492}, 2016.
% [Online]. Available: \url{https://arxiv.org/abs/1610.05492}

% \bibitem{konecny2016fedoptbeyond}
% J.~Kone\v{c}n\'y, H.~B.~McMahan, and D.~Ramage,
% ``Federated optimization: Distributed optimization beyond the datacenter,''
% \emph{arXiv preprint arXiv:1511.03575}, 2016.
% [Online]. Available: \url{https://arxiv.org/abs/1511.03575}


% % ---------------- Communication / compression for distributed & federated training ----------------
% \bibitem{alistarh2017qsgd}
% D.~Alistarh, J.~Li, R.~Tomioka, and M.~Vojnovi\'c,
% ``QSGD: Communication-efficient SGD via gradient quantization and encoding,''
% in \emph{Proc. NeurIPS}, 2017.
% [Online]. Available: \url{https://arxiv.org/abs/1610.02132}

% \bibitem{wen2017terngrad}
% W.~Wen \emph{et al.},
% ``TernGrad: Ternary gradients to reduce communication in distributed deep learning,''
% in \emph{Proc. NeurIPS}, 2017.
% [Online]. Available: \url{https://arxiv.org/abs/1705.07878}

% \bibitem{lin2018dgc}
% Y.~Lin, S.~Han, H.~Mao, Y.~Wang, and W.~J.~Dally,
% ``Deep gradient compression: Reducing the communication bandwidth for distributed training,''
% in \emph{Proc. ICLR}, 2018.
% [Online]. Available: \url{https://arxiv.org/abs/1712.01887}

% \bibitem{bernstein2018signsgd}
% J.~Bernstein \emph{et al.},
% ``signSGD: Compressed optimisation for non-convex problems,''
% in \emph{Proc. ICML}, 2018.
% [Online]. Available: \url{https://arxiv.org/abs/1802.04434}

% \bibitem{karimireddy2019errorfeedback}
% S.~P.~Karimireddy \emph{et al.},
% ``Error feedback fixes SignSGD and other gradient compression schemes,''
% in \emph{Proc. ICML}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1901.09847}

% \bibitem{vogels2019powersgd}
% T.~Vogels \emph{et al.},
% ``PowerSGD: Practical low-rank gradient compression for distributed optimization,''
% in \emph{Proc. NeurIPS}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1905.13727}

% \bibitem{stich2019sparsgd}
% S.~U.~Stich, J.-B.~Cordonnier, and M.~Jaggi,
% ``Sparsified SGD with memory,''
% in \emph{Proc. NeurIPS}, 2018.
% [Online]. Available: \url{https://arxiv.org/abs/1809.07599}

% \bibitem{reisizadeh2020fedpaq}
% A.~Reisizadeh \emph{et al.},
% ``FedPAQ: A communication-efficient federated learning method with periodic averaging and quantization,''
% in \emph{Proc. NeurIPS}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/1909.13014}

% \bibitem{sattler2019stc}
% F.~Sattler, S.~Wiedemann, K.-R.~M\"uller, and W.~Samek,
% ``Sparse binary compression: Towards distributed deep learning with minimal communication,''
% \emph{arXiv preprint arXiv:1903.02891}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1903.02891}

% \bibitem{seide20141bit}
% F.~Seide, H.~Fu, J.~Droppo, G.~Li, and D.~Yu,
% ``1-bit stochastic gradient descent and its application to data-parallel distributed training of speech DNNs,''
% in \emph{Proc. Interspeech}, 2014.
% [Online]. Available: \url{https://www.isca-archive.org/interspeech_2014/seide14_interspeech.html}


% % ---------------- Fisher / second-order / pruning / quantization foundations ----------------
% \bibitem{amari1998natural}
% S.-I.~Amari,
% ``Natural gradient works efficiently in learning,''
% \emph{Neural Computation}, vol.~10, no.~2, pp.~251--276, 1998.
% [Online]. Available: \url{https://doi.org/10.1162/089976698300017746}

% \bibitem{martens2015kfac}
% J.~Martens and R.~Grosse,
% ``Optimizing neural networks with Kronecker-factored approximate curvature,''
% in \emph{Proc. ICML}, 2015.
% [Online]. Available: \url{https://arxiv.org/abs/1503.05671}

% \bibitem{lecun1989obd}
% Y.~LeCun, J.~S.~Denker, and S.~A.~Solla,
% ``Optimal brain damage,''
% in \emph{Advances in Neural Information Processing Systems}, 1989.
% [Online]. Available: \url{https://proceedings.neurips.cc/paper_files/paper/1989/hash/6c9882bbac1c7093bd25041881277658-Abstract.html}

% \bibitem{hassibi1993obs}
% B.~Hassibi and D.~G.~Stork,
% ``Second order derivatives for network pruning: Optimal brain surgeon,''
% in \emph{Advances in Neural Information Processing Systems}, 1993.
% [Online]. Available: \url{https://proceedings.neurips.cc/paper_files/paper/1993/hash/303ed4c69846ab36c2904d3ba8573050-Abstract.html}

% \bibitem{kirkpatrick2017ewc}
% J.~Kirkpatrick \emph{et al.},
% ``Overcoming catastrophic forgetting in neural networks,''
% \emph{PNAS}, 2017.
% [Online]. Available: \url{https://arxiv.org/abs/1612.00796}

% \bibitem{frankle2019lottery}
% J.~Frankle and M.~Carbin,
% ``The lottery ticket hypothesis: Finding sparse, trainable neural networks,''
% in \emph{Proc. ICLR}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1803.03635}

% \bibitem{han2016deepcompression}
% S.~Han, H.~Mao, and W.~J.~Dally,
% ``Deep compression: Compressing deep neural networks with pruning, trained quantization and Huffman coding,''
% in \emph{Proc. ICLR}, 2016.
% [Online]. Available: \url{https://arxiv.org/abs/1510.00149}

% \bibitem{molchanov2017variationaldropout}
% D.~Molchanov, A.~Ashukha, and D.~Vetrov,
% ``Variational dropout sparsifies deep neural networks,''
% in \emph{Proc. ICML}, 2017.
% [Online]. Available: \url{https://arxiv.org/abs/1701.05369}

% \bibitem{lee2019snip}
% N.~Lee, T.~Ajanthan, and P.~H.~S.~Torr,
% ``SNIP: Single-shot network pruning based on connection sensitivity,''
% in \emph{Proc. ICLR}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1810.02340}

% \bibitem{wang2020grasp}
% C.~Wang, G.~Zhang, and R.~Grosse,
% ``Picking winning tickets before training by preserving gradient flow,''
% in \emph{Proc. ICLR}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/2002.07376}

% \bibitem{jacob2018quant}
% B.~Jacob \emph{et al.},
% ``Quantization and training of neural networks for efficient integer-arithmetic-only inference,''
% in \emph{Proc. CVPR}, 2018.
% [Online]. Available: \url{https://arxiv.org/abs/1712.05877}


% % ---------------- PEFT for (federated) fine-tuning LLMs ----------------
% \bibitem{houlsby2019adapters}
% N.~Houlsby \emph{et al.},
% ``Parameter-efficient transfer learning for NLP,''
% in \emph{Proc. ICML}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1902.00751}

% \bibitem{li2021prefix}
% X.~L.~Li and P.~Liang,
% ``Prefix-tuning: Optimizing continuous prompts for generation,''
% in \emph{Proc. ACL}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/2101.00190}

% \bibitem{lester2021prompttuning}
% B.~Lester, R.~Al-Rfou, and N.~Constant,
% ``The power of scale for parameter-efficient prompt tuning,''
% in \emph{Proc. EMNLP}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/2104.08691}

% \bibitem{hu2022lora}
% E.~J.~Hu \emph{et al.},
% ``LoRA: Low-rank adaptation of large language models,''
% in \emph{Proc. ICLR}, 2022.
% [Online]. Available: \url{https://arxiv.org/abs/2106.09685}

% \bibitem{zhang2023adaptive}
% L.~Liu \emph{et al.},
% ``AdaLoRA: Adaptive budget allocation for parameter-efficient fine-tuning,''
% in \emph{Proc. ICLR}, 2023.
% [Online]. Available: \url{https://arxiv.org/abs/2303.10512}


% % ---------------- LLM quantization / efficient deployment (edge-friendly) ----------------
% \bibitem{dettmers2022llmint8}
% T.~Dettmers \emph{et al.},
% ``LLM.int8(): 8-bit matrix multiplication for transformers at scale,''
% \emph{arXiv preprint arXiv:2208.07339}, 2022.
% [Online]. Available: \url{https://arxiv.org/abs/2208.07339}

% \bibitem{frantar2022gptq}
% E.~Frantar, S.~Ashkboos, T.~Hoefler, and D.~Alistarh,
% ``GPTQ: Accurate post-training quantization for generative pre-trained transformers,''
% \emph{arXiv preprint arXiv:2210.17323}, 2022.
% [Online]. Available: \url{https://arxiv.org/abs/2210.17323}

% \bibitem{xiao2023smoothquant}
% G.~Xiao \emph{et al.},
% ``SmoothQuant: Accurate and efficient post-training quantization for large language models,''
% \emph{arXiv preprint arXiv:2211.10438}, 2023.
% [Online]. Available: \url{https://arxiv.org/abs/2211.10438}

% \bibitem{lin2023awq}
% J.~Lin \emph{et al.},
% ``AWQ: Activation-aware weight quantization for LLM compression and acceleration,''
% \emph{arXiv preprint arXiv:2306.00978}, 2023.
% [Online]. Available: \url{https://arxiv.org/abs/2306.00978}

% \bibitem{yao2022zeroquant}
% Z.~Yao \emph{et al.},
% ``ZeroQuant: Efficient and affordable post-training quantization for large-scale transformers,''
% \emph{arXiv preprint arXiv:2206.01861}, 2022.
% [Online]. Available: \url{https://arxiv.org/abs/2206.01861}

% \bibitem{dettmers2023qlora}
% T.~Dettmers \emph{et al.},
% ``QLoRA: Efficient finetuning of quantized LLMs,''
% \emph{arXiv preprint arXiv:2305.14314}, 2023.
% [Online]. Available: \url{https://arxiv.org/abs/2305.14314}


% % ---------------- Core Transformer / LLM foundations ----------------
% \bibitem{vaswani2017attention}
% A.~Vaswani \emph{et al.},
% ``Attention is all you need,''
% in \emph{Proc. NeurIPS}, 2017.
% [Online]. Available: \url{https://arxiv.org/abs/1706.03762}

% \bibitem{devlin2019bert}
% J.~Devlin, M.-W.~Chang, K.~Lee, and K.~Toutanova,
% ``BERT: Pre-training of deep bidirectional transformers for language understanding,''
% in \emph{Proc. NAACL}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1810.04805}

% \bibitem{brown2020gpt3}
% T.~B.~Brown \emph{et al.},
% ``Language models are few-shot learners,''
% in \emph{Proc. NeurIPS}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/2005.14165}

% \bibitem{touvron2023llama}
% H.~Touvron \emph{et al.},
% ``LLaMA: Open and efficient foundation language models,''
% \emph{arXiv preprint arXiv:2302.13971}, 2023.
% [Online]. Available: \url{https://arxiv.org/abs/2302.13971}


% % ---------------- Efficient ViT / token reduction (EViT / A-ViT / ToMe fixed) ----------------
% \bibitem{dosovitskiy2021vit}
% A.~Dosovitskiy \emph{et al.},
% ``An image is worth 16x16 words: Transformers for image recognition at scale,''
% in \emph{Proc. ICLR}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/2010.11929}

% \bibitem{rao2021dynamicvit}
% Y.~Rao \emph{et al.},
% ``DynamicViT: Efficient vision transformers with dynamic token sparsification,''
% in \emph{Proc. NeurIPS}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/2106.02034}

% \bibitem{ryoo2021tokenlearner}
% M.~S.~Ryoo \emph{et al.},
% ``TokenLearner: What can 8 learned tokens do for images and videos?,''
% in \emph{Proc. NeurIPS}, 2021.
% [Online]. Available: \url{https://arxiv.org/abs/2106.11297}

% \bibitem{fayyaz2022ats}
% M.~Fayyaz \emph{et al.},
% ``Adaptive token sampling for efficient vision transformers,''
% in \emph{Proc. ECCV}, 2022.
% [Online]. Available: \url{https://arxiv.org/abs/2111.15667}

% \bibitem{liang2022evit}
% Y.~Liang \emph{et al.},
% ``Not all patches are what you need: Expediting vision transformers via token reorganizations,''
% in \emph{Proc. ICLR}, 2022.
% [Online]. Available: \url{https://arxiv.org/abs/2202.07800}

% \bibitem{yin2022avit}
% H.~Yin \emph{et al.},
% ``A-ViT: Adaptive tokens for efficient vision transformer,''
% in \emph{Proc. CVPR}, 2022, pp.~10809--10818.
% [Online]. Available: \url{https://github.com/NVlabs/A-ViT}
% % Accessed: YYYY-MM-DD.

% \bibitem{bolya2022tome}
% D.~Bolya \emph{et al.},
% ``Token merging: Your ViT but faster,''
% \emph{arXiv preprint arXiv:2210.09461}, 2022.
% [Online]. Available: \url{https://arxiv.org/abs/2210.09461}


% % ---------------- Evaluation datasets (your QA experiments) ----------------
% \bibitem{jin2019pubmedqa}
% Q.~Jin, B.~Dhingra, Z.~Liu, W.~W.~Cohen, and X.~Lu,
% ``PubMedQA: A dataset for biomedical research question answering,''
% in \emph{Proc. EMNLP-IJCNLP}, 2019.
% [Online]. Available: \url{https://arxiv.org/abs/1909.06146}

% \bibitem{jin2020medqa}
% D.~Jin, E.~Pan, N.~Oufattole, W.-H.~Weng, H.~Fang, and P.~Szolovits,
% ``What disease does this patient have? A large-scale open domain question answering dataset from medical exams,''
% \emph{arXiv preprint arXiv:2009.13081}, 2020.
% [Online]. Available: \url{https://arxiv.org/abs/2009.13081}


% % ---------------- arXiv:2601.21293 ----------------
% \bibitem{li2026pgtmt}
% C.~Li \emph{et al.},
% ``Physics-guided tiny-mamba transformer for reliability-aware early fault warning,''
% \emph{arXiv preprint arXiv:2601.21293}, 2026.
% [Online]. Available: \url{https://arxiv.org/abs/2601.21293}

% \end{thebibliography}

% biography section
% 
% If you have an EPS/PDF photo (graphicx package needed) extra braces are
% needed around the contents of the optional argument to biography to prevent
% the LaTeX parser from getting confused when it sees the complicated
% simpler here.)
% or if you just want to reserve a space for a photo:


% Generated by IEEEtran.bst, version: 1.14 (2015/08/26)
\begin{thebibliography}{10}
\providecommand{\url}[1]{#1}
\csname url@samestyle\endcsname
\providecommand{\newblock}{\relax}
\providecommand{\bibinfo}[2]{#2}
\providecommand{\BIBentrySTDinterwordspacing}{\spaceskip=0pt\relax}
\providecommand{\BIBentryALTinterwordstretchfactor}{4}
\providecommand{\BIBentryALTinterwordspacing}{\spaceskip=\fontdimen2\font plus
\BIBentryALTinterwordstretchfactor\fontdimen3\font minus
  \fontdimen4\font\relax}
\providecommand{\BIBforeignlanguage}[2]{{%
\expandafter\ifx\csname l@#1\endcsname\relax
\typeout{** WARNING: IEEEtran.bst: No hyphenation pattern has been}%
\typeout{** loaded for the language `#1'. Using the pattern for}%
\typeout{** the default language instead.}%
\else
\language=\csname l@#1\endcsname
\fi
#2}}
\providecommand{\BIBdecl}{\relax}
\BIBdecl

\bibitem{brown2020gpt3}
T.~Brown, B.~Mann, N.~Ryder \emph{et~al.}, ``Language models are few-shot
  learners,'' \emph{Advances in neural information processing systems},
  vol.~33, pp. 1877--1901, 2020.

\bibitem{touvron2023llama}
H.~Touvron, T.~Lavril, G.~Izacard \emph{et~al.}, ``Llama: Open and efficient
  foundation language models,'' \emph{arXiv preprint arXiv:2302.13971}, 2023.

\bibitem{devlin2019bert}
J.~Devlin, M.-W. Chang, K.~Lee \emph{et~al.}, ``Bert: Pre-training of deep
  bidirectional transformers for language understanding,'' in \emph{Proceedings
  of the 2019 conference of the North American chapter of the association for
  computational linguistics: human language technologies, volume 1 (long and
  short papers)}, 2019, pp. 4171--4186.

\bibitem{vaswani2017attention}
A.~Vaswani, N.~Shazeer, N.~Parmar \emph{et~al.}, ``Attention is all you need,''
  \emph{Advances in neural information processing systems}, vol.~30, 2017.

\bibitem{shi2016edge}
W.~Shi, J.~Cao, Q.~Zhang \emph{et~al.}, ``Edge computing: Vision and
  challenges,'' \emph{IEEE internet of things journal}, vol.~3, no.~5, pp.
  637--646, 2016.

\bibitem{mcm2017fedavg}
B.~McMahan, E.~Moore, D.~Ramage \emph{et~al.}, ``Communication-efficient
  learning of deep networks from decentralized data,'' in \emph{Artificial
  intelligence and statistics}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR,
  2017, pp. 1273--1282.

\bibitem{kairouz2021flsurvey}
P.~Kairouz, H.~B. McMahan, B.~Avent \emph{et~al.}, ``Advances and open problems
  in federated learning,'' \emph{Foundations and trends{\textregistered} in
  machine learning}, vol.~14, no. 1--2, pp. 1--210, 2021.

\bibitem{li2020flspm}
T.~Li, A.~K. Sahu, A.~Talwalkar \emph{et~al.}, ``Federated learning:
  Challenges, methods, and future directions,'' \emph{IEEE signal processing
  magazine}, vol.~37, no.~3, pp. 50--60, 2020.

\bibitem{bonawitz2017secureagg}
K.~Bonawitz, V.~Ivanov, B.~Kreuter \emph{et~al.}, ``Practical secure
  aggregation for privacy-preserving machine learning,'' in \emph{proceedings
  of the 2017 ACM SIGSAC Conference on Computer and Communications Security},
  2017, pp. 1175--1191.

\bibitem{abadi2016dpsgd}
M.~Abadi, A.~Chu, I.~Goodfellow \emph{et~al.}, ``Deep learning with
  differential privacy,'' in \emph{Proceedings of the 2016 ACM SIGSAC
  conference on computer and communications security}, 2016, pp. 308--318.

\bibitem{lim2020fedcomst}
W.~Y.~B. Lim, N.~C. Luong, D.~T. Hoang \emph{et~al.}, ``Federated learning in
  mobile edge networks: A comprehensive survey,'' \emph{IEEE communications
  surveys \& tutorials}, vol.~22, no.~3, pp. 2031--2063, 2020.

\bibitem{bonawitz2019flsystems}
K.~Bonawitz, H.~Eichner, W.~Grieskamp \emph{et~al.}, ``Towards federated
  learning at scale: System design,'' \emph{Proceedings of machine learning and
  systems}, vol.~1, pp. 374--388, 2019.

\bibitem{hu2022lora}
\BIBentryALTinterwordspacing
E.~J. Hu, yelong shen, P.~Wallis \emph{et~al.}, ``Lo{RA}: Low-rank adaptation
  of large language models,'' in \emph{International Conference on Learning
  Representations}, 2022. [Online]. Available:
  \url{https://openreview.net/forum?id=nZeVKeeFYf9}
\BIBentrySTDinterwordspacing

\bibitem{dettmers2023qlora}
T.~Dettmers, A.~Pagnoni, A.~Holtzman \emph{et~al.}, ``Qlora: Efficient
  finetuning of quantized llms,'' \emph{Advances in neural information
  processing systems}, vol.~36, pp. 10\,088--10\,115, 2023.

\bibitem{li2020fedprox}
T.~Li, A.~K. Sahu, M.~Zaheer \emph{et~al.}, ``Federated optimization in
  heterogeneous networks,'' \emph{Proceedings of Machine learning and systems},
  vol.~2, pp. 429--450, 2020.

\bibitem{wang2020fednova}
J.~Wang, Q.~Liu, H.~Liang \emph{et~al.}, ``Tackling the objective inconsistency
  problem in heterogeneous federated optimization,'' \emph{Advances in neural
  information processing systems}, vol.~33, pp. 7611--7623, 2020.

\bibitem{karimireddy2020scaffold}
S.~P. Karimireddy, S.~Kale, M.~Mohri \emph{et~al.}, ``Scaffold: Stochastic
  controlled averaging for federated learning,'' in \emph{International
  conference on machine learning}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR,
  2020, pp. 5132--5143.

\bibitem{reddi2021fedopt}
\BIBentryALTinterwordspacing
S.~J. Reddi, Z.~Charles, M.~Zaheer \emph{et~al.}, ``Adaptive federated
  optimization,'' in \emph{International Conference on Learning
  Representations}, 2021. [Online]. Available:
  \url{https://openreview.net/forum?id=LkFG3lB13U5}
\BIBentrySTDinterwordspacing

\bibitem{acar2021feddyn}
\BIBentryALTinterwordspacing
D.~A.~E. Acar, Y.~Zhao, R.~Matas \emph{et~al.}, ``Federated learning based on
  dynamic regularization,'' in \emph{International Conference on Learning
  Representations}, 2021. [Online]. Available:
  \url{https://openreview.net/forum?id=B7v4QMR6Z9w}
\BIBentrySTDinterwordspacing

\bibitem{caldas2018leaf}
S.~Caldas, S.~M.~K. Duddu, P.~Wu \emph{et~al.}, ``Leaf: A benchmark for
  federated settings,'' \emph{arXiv preprint arXiv:1812.01097}, 2018.

\bibitem{hsieh2021fedscale}
F.~Lai, Y.~Dai, S.~Singapuram \emph{et~al.}, ``Fedscale: Benchmarking model and
  system performance of federated learning at scale,'' in \emph{International
  conference on machine learning}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR,
  2022, pp. 11\,814--11\,827.

\bibitem{beutel2020flower}
D.~J. Beutel, T.~Topal, A.~Mathur \emph{et~al.}, ``Flower: A friendly federated
  learning research framework,'' \emph{arXiv preprint arXiv:2007.14390}, 2020.

\bibitem{alistarh2017qsgd}
D.~Alistarh, D.~Grubic, J.~Li \emph{et~al.}, ``Qsgd: Communication-efficient
  sgd via gradient quantization and encoding,'' \emph{Advances in neural
  information processing systems}, vol.~30, 2017.

\bibitem{lin2018dgc}
\BIBentryALTinterwordspacing
Y.~Lin, S.~Han, H.~Mao \emph{et~al.}, ``Deep gradient compression: Reducing the
  communication bandwidth for distributed training,'' in \emph{International
  Conference on Learning Representations}, 2018. [Online]. Available:
  \url{https://openreview.net/forum?id=SkhQHMW0W}
\BIBentrySTDinterwordspacing

\bibitem{reisizadeh2020fedpaq}
A.~Reisizadeh, A.~Mokhtari, H.~Hassani \emph{et~al.}, ``Fedpaq: A
  communication-efficient federated learning method with periodic averaging and
  quantization,'' in \emph{International conference on artificial intelligence
  and statistics}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR, 2020, pp.
  2021--2031.

\bibitem{karimireddy2019errorfeedback}
S.~P. Karimireddy, Q.~Rebjock, S.~Stich \emph{et~al.}, ``Error feedback fixes
  signsgd and other gradient compression schemes,'' in \emph{International
  conference on machine learning}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR,
  2019, pp. 3252--3261.

\bibitem{rao2021dynamicvit}
Y.~Rao, W.~Zhao, B.~Liu \emph{et~al.}, ``Dynamicvit: Efficient vision
  transformers with dynamic token sparsification,'' \emph{Advances in neural
  information processing systems}, vol.~34, pp. 13\,937--13\,949, 2021.

\bibitem{bolya2022tome}
D.~Bolya, C.-Y. Fu, X.~Dai \emph{et~al.}, ``Token merging: Your vit but
  faster,'' \emph{arXiv preprint arXiv:2210.09461}, 2022.

\bibitem{dettmers2022llmint8}
T.~Dettmers, M.~Lewis, Y.~Belkada \emph{et~al.}, ``Llm. int8 () 8-bit matrix
  multiplication for transformers at scale,'' in \emph{Proceedings of the 36th
  International Conference on Neural Information Processing Systems}, 2022, pp.
  30\,318--30\,332.

\bibitem{frantar2022gptq}
E.~Frantar, S.~Ashkboos, T.~Hoefler \emph{et~al.}, ``Gptq: Accurate
  post-training quantization for generative pre-trained transformers,''
  \emph{arXiv preprint arXiv:2210.17323}, 2022.

\bibitem{xiao2023smoothquant}
G.~Xiao, J.~Lin, M.~Seznec \emph{et~al.}, ``Smoothquant: Accurate and efficient
  post-training quantization for large language models,'' in
  \emph{International conference on machine learning}.\hskip 1em plus 0.5em
  minus 0.4em\relax PMLR, 2023, pp. 38\,087--38\,099.

\bibitem{lin2023awq}
J.~Lin, J.~Tang, H.~Tang \emph{et~al.}, ``Awq: Activation-aware weight
  quantization for on-device llm compression and acceleration,''
  \emph{Proceedings of machine learning and systems}, vol.~6, pp. 87--100,
  2024.

\bibitem{yao2022zeroquant}
Z.~Yao, R.~Yazdani~Aminabadi, M.~Zhang \emph{et~al.}, ``Zeroquant: Efficient
  and affordable post-training quantization for large-scale transformers,''
  \emph{Advances in neural information processing systems}, vol.~35, pp.
  27\,168--27\,183, 2022.

\bibitem{amari1998natural}
S.-I. Amari, ``Natural gradient works efficiently in learning,'' \emph{Neural
  computation}, vol.~10, no.~2, pp. 251--276, 1998.

\bibitem{martens2015kfac}
J.~Martens and R.~Grosse, ``Optimizing neural networks with kronecker-factored
  approximate curvature,'' in \emph{International conference on machine
  learning}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR, 2015, pp. 2408--2417.

\bibitem{lecun1989obd}
Y.~LeCun, J.~Denker, and S.~Solla, ``Optimal brain damage,'' \emph{Advances in
  neural information processing systems}, vol.~2, 1989.

\bibitem{hassibi1993obs}
B.~Hassibi and D.~Stork, ``Second order derivatives for network pruning:
  Optimal brain surgeon,'' \emph{Advances in neural information processing
  systems}, vol.~5, 1992.

\bibitem{kirkpatrick2017ewc}
J.~Kirkpatrick, R.~Pascanu, N.~Rabinowitz \emph{et~al.}, ``Overcoming
  catastrophic forgetting in neural networks,'' \emph{Proceedings of the
  national academy of sciences}, vol. 114, no.~13, pp. 3521--3526, 2017.

\bibitem{lee2019snip}
\BIBentryALTinterwordspacing
N.~Lee, T.~Ajanthan, and P.~Torr, ``{SNIP}: {SINGLE}-{SHOT} {NETWORK} {PRUNING}
  {BASED} {ON} {CONNECTION} {SENSITIVITY},'' in \emph{International Conference
  on Learning Representations}, 2019. [Online]. Available:
  \url{https://openreview.net/forum?id=B1VZqjAcYX}
\BIBentrySTDinterwordspacing

\bibitem{wang2020grasp}
\BIBentryALTinterwordspacing
C.~Wang, G.~Zhang, and R.~Grosse, ``Picking winning tickets before training by
  preserving gradient flow,'' in \emph{International Conference on Learning
  Representations}, 2020. [Online]. Available:
  \url{https://openreview.net/forum?id=SkgsACVKPH}
\BIBentrySTDinterwordspacing

\bibitem{jin2019pubmedqa}
Q.~Jin, B.~Dhingra, Z.~Liu \emph{et~al.}, ``Pubmedqa: A dataset for biomedical
  research question answering,'' in \emph{Proceedings of the 2019 conference on
  empirical methods in natural language processing and the 9th international
  joint conference on natural language processing (EMNLP-IJCNLP)}, 2019, pp.
  2567--2577.

\bibitem{jin2020medqa}
D.~Jin, E.~Pan, N.~Oufattole \emph{et~al.}, ``What disease does this patient
  have? a large-scale open domain question answering dataset from medical
  exams,'' \emph{Applied Sciences}, vol.~11, no.~14, p. 6421, 2021.

\bibitem{konecny2016fedoptbeyond}
J.~Kone{\v{c}}n{\`y}, B.~McMahan, and D.~Ramage, ``Federated optimization:
  Distributed optimization beyond the datacenter,'' \emph{arXiv preprint
  arXiv:1511.03575}, 2015.

\bibitem{konecny2016comm}
J.~Kone{\v{c}}n{\`y}, H.~B. McMahan, F.~X. Yu \emph{et~al.}, ``Federated
  learning: Strategies for improving communication efficiency,'' \emph{arXiv
  preprint arXiv:1610.05492}, 2016.

\bibitem{wen2017terngrad}
W.~Wen, C.~Xu, F.~Yan \emph{et~al.}, ``Terngrad: Ternary gradients to reduce
  communication in distributed deep learning,'' \emph{Advances in neural
  information processing systems}, vol.~30, 2017.

\bibitem{seide20141bit}
F.~Seide, H.~Fu, J.~Droppo \emph{et~al.}, ``1-bit stochastic gradient descent
  and its application to data-parallel distributed training of speech dnns.''
  in \emph{Interspeech}, vol. 2014.\hskip 1em plus 0.5em minus 0.4em\relax
  Singapore, 2014, pp. 1058--1062.

\bibitem{bernstein2018signsgd}
J.~Bernstein, Y.-X. Wang, K.~Azizzadenesheli \emph{et~al.}, ``signsgd:
  Compressed optimisation for non-convex problems,'' in \emph{International
  conference on machine learning}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR,
  2018, pp. 560--569.

\bibitem{li2024fedbat}
S.~Li, W.~Xu, H.~Wang \emph{et~al.}, ``Fedbat: Communication-efficient
  federated learning via learnable binarization,'' \emph{arXiv preprint
  arXiv:2408.03215}, 2024, accepted by ICML 2024 (as stated on arXiv).

\bibitem{stich2019sparsgd}
S.~U. Stich, J.-B. Cordonnier, and M.~Jaggi, ``Sparsified sgd with memory,''
  \emph{Advances in neural information processing systems}, vol.~31, 2018.

\bibitem{sattler2019stc}
F.~Sattler, S.~Wiedemann, K.-R. M{\"u}ller \emph{et~al.}, ``Sparse binary
  compression: Towards distributed deep learning with minimal communication,''
  in \emph{2019 International Joint Conference on Neural Networks
  (IJCNN)}.\hskip 1em plus 0.5em minus 0.4em\relax IEEE, 2019, pp. 1--8.

\bibitem{vogels2019powersgd}
T.~Vogels, S.~P. Karimireddy, and M.~Jaggi, ``Powersgd: Practical low-rank
  gradient compression for distributed optimization,'' \emph{Advances in Neural
  Information Processing Systems}, vol.~32, 2019.

\bibitem{houlsby2019adapters}
N.~Houlsby, A.~Giurgiu, S.~Jastrzebski \emph{et~al.}, ``Parameter-efficient
  transfer learning for nlp,'' in \emph{International conference on machine
  learning}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR, 2019, pp. 2790--2799.

\bibitem{li2021prefix}
X.~L. Li and P.~Liang, ``Prefix-tuning: Optimizing continuous prompts for
  generation,'' in \emph{Proceedings of the 59th Annual Meeting of the
  Association for Computational Linguistics and the 11th International Joint
  Conference on Natural Language Processing (Volume 1: Long Papers)}, 2021, pp.
  4582--4597.

\bibitem{lester2021prompttuning}
B.~Lester, R.~Al-Rfou, and N.~Constant, ``The power of scale for
  parameter-efficient prompt tuning,'' in \emph{Proceedings of the 2021
  Conference on Empirical Methods in Natural Language Processing}, 2021, pp.
  3045--3059.

\bibitem{zhang2023adaptive}
\BIBentryALTinterwordspacing
Q.~Zhang, M.~Chen, A.~Bukharin \emph{et~al.}, ``Adaptive budget allocation for
  parameter-efficient fine-tuning,'' in \emph{The Eleventh International
  Conference on Learning Representations}, 2023. [Online]. Available:
  \url{https://openreview.net/forum?id=lq62uWRJjiY}
\BIBentrySTDinterwordspacing

\bibitem{han2016deepcompression}
\BIBentryALTinterwordspacing
S.~Han, H.~Mao, and W.~J. Dally, ``Deep compression: Compressing deep neural
  network with pruning, trained quantization and huffman coding,'' in
  \emph{ICLR}, 2016. [Online]. Available: \url{http://arxiv.org/abs/1510.00149}
\BIBentrySTDinterwordspacing

\bibitem{jacob2018quant}
B.~Jacob, S.~Kligys, B.~Chen \emph{et~al.}, ``Quantization and training of
  neural networks for efficient integer-arithmetic-only inference,'' in
  \emph{Proceedings of the IEEE conference on computer vision and pattern
  recognition}, 2018, pp. 2704--2713.

\bibitem{molchanov2017variationaldropout}
D.~Molchanov, A.~Ashukha, and D.~Vetrov, ``Variational dropout sparsifies deep
  neural networks,'' in \emph{International conference on machine
  learning}.\hskip 1em plus 0.5em minus 0.4em\relax PMLR, 2017, pp. 2498--2507.

\bibitem{frankle2019lottery}
\BIBentryALTinterwordspacing
J.~Frankle and M.~Carbin, ``The lottery ticket hypothesis: Finding sparse,
  trainable neural networks,'' in \emph{International Conference on Learning
  Representations}, 2019. [Online]. Available:
  \url{https://openreview.net/forum?id=rJl-b3RcF7}
\BIBentrySTDinterwordspacing

\bibitem{dosovitskiy2021vit}
\BIBentryALTinterwordspacing
A.~Dosovitskiy, L.~Beyer, A.~Kolesnikov \emph{et~al.}, ``An image is worth
  16x16 words: Transformers for image recognition at scale,'' in
  \emph{International Conference on Learning Representations}, 2021. [Online].
  Available: \url{https://openreview.net/forum?id=YicbFdNTTy}
\BIBentrySTDinterwordspacing

\bibitem{ryoo2021tokenlearner}
M.~S. Ryoo, A.~Piergiovanni, A.~Arnab \emph{et~al.}, ``Tokenlearner: Adaptive
  space-time tokenization for videos,'' in \emph{Advances in Neural Information
  Processing Systems (NeurIPS)}, 2021.

\bibitem{fayyaz2022ats}
M.~Fayyaz, S.~A. Koohpayegani, F.~R. Jafari \emph{et~al.}, ``Adaptive token
  sampling for efficient vision transformers,'' in \emph{European conference on
  computer vision}.\hskip 1em plus 0.5em minus 0.4em\relax Springer, 2022, pp.
  396--414.

\bibitem{yin2022avit}
H.~Yin, A.~Vahdat, J.~M. Alvarez \emph{et~al.}, ``A-vit: Adaptive tokens for
  efficient vision transformer,'' in \emph{Proceedings of the IEEE/CVF
  conference on computer vision and pattern recognition}, 2022, pp.
  10\,809--10\,818.

\bibitem{liang2022evit}
\BIBentryALTinterwordspacing
Y.~Liang, C.~GE, Z.~Tong \emph{et~al.}, ``{EV}it: Expediting vision
  transformers via token reorganizations,'' in \emph{International Conference
  on Learning Representations}, 2022. [Online]. Available:
  \url{https://openreview.net/forum?id=BjyvwnXXVn_}
\BIBentrySTDinterwordspacing

\bibitem{li2026pgtmt}
C.~Li, D.~Huang, K.~Yao \emph{et~al.}, ``Physics-guided tiny-mamba transformer
  for reliability-aware early fault warning,'' \emph{arXiv preprint
  arXiv:2601.21293}, 2026.

\end{thebibliography}

% ====================================




\end{document}


