 \documentclass[lettersize,journal]{IEEEtran}
\usepackage{amsmath,amsfonts}
\usepackage{array}
\usepackage[caption=false,font=normalsize,labelfont=sf,textfont=sf]{subfig}
\usepackage{textcomp}
\usepackage{stfloats}
\usepackage{url}
\usepackage{verbatim}
\usepackage{graphicx}
\usepackage{cite}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage[table,xcdraw]{xcolor}
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{algpseudocode}
\algrenewcommand\algorithmicrequire{\textbf{Input:}}
\algrenewcommand\algorithmicensure{\textbf{Output:}}
\usepackage{algorithm}
\usepackage{bm}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{makecell}
\usepackage{xcolor}
\hyphenation{op-tical net-works semi-conduc-tor IEEE-Xplore}
% updated with editorial comments 8/9/2021

\begin{document}

\title{EvoTSC: Evolving Feature Learning Models for Time Series Classification via Genetic Programming}

\author{Xuanhao Yang, Bing Xue, \IEEEmembership{Fellow, IEEE}, and Mengjie Zhang, \IEEEmembership{Fellow, IEEE}
	\thanks{This work has been submitted to the IEEE for possible publication. Copyright may be transferred without notice, after which this version may no longer be accessible.}%
	\thanks{Xuanhao Yang, Bing Xue, and Mengjie Zhang are with the Centre for Data Science and Artificial Intelligence \& School of Engineering and Computer Science, Victoria University of Wellington, PO Box 600, Wellington 6140, New Zealand (e-mails: xuanhao.yang@vuw.ac.nz; bing.xue@ecs.vuw.ac.nz; and mengjie.zhang@ecs.vuw.ac.nz).}%
}

\maketitle

\begin{abstract}
Time series classification is an important analytical task across diverse domains. However, its practical application is often hindered by the scarcity of labeled data and the requirement for substantial computational resources. To address these challenges, this paper proposes EvoTSC, a novel genetic programming approach designed to automatically evolve lightweight feature learning models for time series classification. The core of EvoTSC is a carefully designed multi-layer program structure that strategically embeds diverse forms of prior expert knowledge into the evolutionary process, effectively guiding the search toward operations known to be highly effective for time series analysis. To mitigate the common overfitting problem  in time series classification, a tailored Pareto tournament selection strategy is proposed to favor models that perform consistently well across varying training data subsets, promoting the discovery of highly generalizable models. Extensive experiments conducted on univariate time series classification datasets demonstrate that EvoTSC significantly outperforms eleven benchmark methods in most comparisons. Further analyses verify the contribution of each component and the resource efficiency of the evolved models.
\end{abstract}

\begin{IEEEkeywords}
Genetic programming, feature learning, classification, evolutionary machine learning, time series.
\end{IEEEkeywords}

\section{Introduction}
\label{s1}
Time series classification (TSC), the task of assigning categorical labels to temporal sequences, plays a critical role in diverse domains, including medical diagnosis \cite{lin2019medical}, industrial monitoring \cite{polge2020case}, and financial analysis \cite{liang2023improving}. Compared with images and text, time series data lack intuitive semantic clarity, making accurate annotation heavily reliant on costly domain expertise. Consequently, label scarcity is a common challenge in real-world TSC tasks \cite{LTSRL,TSPM}. To overcome this challenge, feature-based TSC approaches have attracted considerable attention \cite{FeaTSC}. By learning discriminative representations guided by explicit objective functions, these methods offer strong potential for facilitating downstream classification even under limited labeled data.

Early explorations in this area relied heavily on domain expertise to design and extract hand-crafted features \cite{catch22}. Such approaches typically summarize raw time series by computing a fixed set of attributes, such as statistical characteristics (e.g., median, maximum), shape descriptors (e.g., slope), and autocorrelation coefficients \cite{tsfel}. A notable strength of these methods lies in their high interpretability, as the extracted features can carry clear physical or statistical meaning \cite{hctsa}. However, relying on a fixed set of predefined features for datasets from various domains inherently limits model flexibility and adaptability.

Recent advancements in feature-based TSC methods have shifted from typical hand-crafted feature extraction toward neural network-based feature learning \cite{ts2vec,frera}. These approaches commonly pre-train a neural network (NN) with a self-supervised objective, preventing the learned features from being overly tailored to specific decision boundaries and thereby enhancing generalizability to the downstream classification task \cite{Kang2020Decoupling,cbd}. Due to the extensive parameter space, these methods can learn flexible, dataset-adaptive features, yielding enhanced classification performance. Following this trend, large foundation models with substantially greater parameter counts are increasingly being explored for TSC \cite{mantis,moment}. While the large scale of these models makes pre-training on the target dataset alone insufficient, it also enables them to leverage large-scale external data for pre-training, producing transferable features for the target task \cite{tivit}.

While neural network-based approaches, including foundation models, have achieved remarkable success in learning discriminative features, several fundamental limitations remain. First, the large number of parameters demands substantial computational resources for inference, posing practical challenges for deployment in resource-constrained environments, such as wearable health devices \cite{ECGTCN} and industrial monitoring sensors \cite{saeed2025deep}. Second, these approaches typically operate as black-box systems with limited interpretability, which is a significant concern in safety-critical applications \cite{interpretable}. These limitations collectively motivate the exploration of an alternative paradigm.

Genetic programming (GP) is an evolutionary computation technique inspired by the principles of natural selection \cite{banzhaf1998genetic,tevc3,zhangtevc1}. By embedding domain-specific knowledge within carefully designed program structures, GP has been successfully applied to feature learning tasks across diverse domains \cite{bimtask,wutevc,peng2}. Within these methods, a GP individual is an explicit composition of executable operations. Each learned feature can be traced back to a concrete sequence of transformations, making the resulting models potentially interpretable \cite{wutevc,bitevc}. Moreover, GP solutions are highly lightweight: once evolution finishes, prediction reduces to executing a compact model, eliminating the need for substantial computational resources and high inference latency \cite{11030860,srlinear}.

Although GP has strong potential to address these limitations, research on GP for feature learning specifically tailored to TSC remains very limited. To bridge this gap, this paper proposes EvoTSC, a GP-based method designed to evolve lightweight and effective feature learning models for TSC. The approach is built upon a novel multi-layer GP program structure that systematically organizes segment detection, domain transform, content-adaptive patching, feature extraction, and feature concatenation into a hierarchical search space. This structural design aims to embed diverse forms of prior expert knowledge directly into the evolutionary process. Meanwhile, to mitigate the common overfitting problem in TSC tasks, a tailored modification to the Pareto tournament selection \cite{paretotournament} is introduced, designed to promote the evolution of models that perform consistently well across varying training data subsets. In this work, we focus on equal-length univariate time series classification. This scope allows us to rigorously evaluate the effectiveness of the proposed evolutionary approach without the interference of cross-variable dependencies or varying sequence lengths. The main objectives are summarized as follows:
\begin{enumerate}
	\item Propose a novel multi-layer program structure specifically designed for feature learning in TSC, enabling the evolution of lightweight and effective feature learning models.
	\item Explore an improved selection strategy to mitigate the overfitting problem commonly encountered in TSC from an evolutionary perspective.
	\item Conduct comparative experiments against eleven benchmark methods to evaluate the effectiveness of the evolved feature learning models, and perform further analyses to verify the contribution of each component and the resource efficiency of the evolved models.
\end{enumerate}

\section{Related Work}
\label{s2}
\subsection{Feature-based Time Series Classification Approaches}
The primary objective of feature-based time series classification approaches is to transform a time series into discriminative feature vectors, thereby enhancing the performance of downstream classification tasks. This subsection reviews typical work of three different kinds of approaches.

\subsubsection{Hand-crafted Feature Extraction Approaches}
A foundational work in this area is hctsa \cite{hctsa}, which consolidates decades of interdisciplinary time series analysis methods into a large, interpretable feature library, computing over 7{,}700 features per input series. Building upon the hctsa library, catch22 \cite{catch22} addresses the computational overhead and feature redundancy of such large-scale feature sets by distilling a compact canonical subset. Another widely used approach is TSFresh \cite{tsfresh}, which offers an intermediate feature dimensionality between hctsa and catch22 by computing a pre-defined set of features spanning the temporal, statistical, and frequency domains. While computationally efficient and interpretable, handcrafted features are inherently static and heavily reliant on domain expertise. Without data-driven optimization to adapt to dataset-specific distributions, these methods inevitably yield irrelevant features.

\subsubsection{Neural Network-based Approaches}
To overcome the issues of hand-crafted features, recent methods employ neural network pre-trained with self-supervised objectives to learn adaptive features directly from data. Among these, contrastive learning is a widely adopted paradigm, aiming to shape the latent space by pulling together semantically similar views while pushing apart dissimilar ones \cite{softclt}. For instance, Yue et al. \cite{ts2vec} propose a hierarchical contrastive framework that contrasts augmented context views across multiple temporal resolutions, enabling the model to capture contextual information at different granularities. From a frequency-domain perspective, Tian et al. \cite{frera} argue that frequency representations exhibit desirable properties for constructing semantic-preserving views and propose a frequency-refined augmentation strategy. This strategy separates and preserves important frequency components while adaptively modifying the remaining ones. Beyond contrastive learning, masked modeling methods represent another popular paradigm, which trains models to reconstruct missing content from visible context, thereby encouraging the learned features to preserve the underlying structure \cite{simmtm}. Cheng et al. \cite{timemae} propose a representative method that employs a decoupled architecture, consisting of a visible encoder that processes only the unmasked patches and a masked decoder that reconstructs the missing portions, facilitating effective feature learning. Moreover, Han et al. \cite{cbd} address the issues of feature homogenization and spectral bias by introducing an auxiliary content-aware balanced decoder. This module adapts interactions to local content variations and explicitly rebalances spectral energy.

\subsubsection{Foundation Model-based Approaches}
Different from the above NN-based methods that training a model solely on the target dataset, foundation model approaches involve pre-training on vast external datasets to extract highly transferable features. A notable example is Mantis \cite{mantis}, a lightweight time series foundation model (TSFM) specialized for TSC tasks. Built upon a vision Transformer (ViT) backbone and pre-trained via contrastive learning on seven million time series samples, Mantis achieves remarkable zero-shot classification performance. Furthermore, TiViT \cite{tivit} explores a cross-modality strategy by transforming one-dimensional time series into two-dimensional images. This allows the model to leverage the representational power of large-scale ViT pre-trained on billions of natural images. 

In summary, NN-based feature learning approaches, including foundation models, have achieved remarkable success in learning flexible and discriminative features. However, these models typically operate as black boxes \cite{interpretable} and demand substantial computational resources during inference. These limitations collectively motivate the exploration of alternative paradigms that offer inherent interpretability while remaining sufficiently lightweight for resource-constrained TSC applications.

\subsection{GP for Feature Learning}
GP has been widely applied to feature learning tasks, demonstrating strong potential particularly in classification problems \cite{tevc0,11417994,peng1}. By embedding domain-specific knowledge into the evolutionary process, GP can automatically evolve explicit compositions of executable operations, producing features that are both effective and potentially interpretable.

Several representative works illustrate how explicitly incorporating such domain knowledge drives the success of GP across diverse classification tasks. In image classification, Bi et al. \cite{bitevc} integrate image-specific operators such as image filtering and pooling into a flexible GP representation, enabling the evolution of variable-depth trees that learn varying numbers and types of features. Similarly, Wang et al. \cite{wangtevc} develop a GP method for fine-grained image classification that explicitly incorporates visual prior knowledge into the search space. By guiding the evolutionary search to focus on object-aware local regions alongside color, shape, and texture cues, this approach improves both the discriminative power and interpretability of the learned features. In multimodal medical image classification, Wu et al.~\cite{wutevc} propose a multitree GP framework that incorporates a slice selection factor based on the clinical insight that only a few image slices are diagnostically informative. The evolved individuals can be inspected to reveal which slices and anatomical regions are used and how modality-specific features are fused, enabling verification against established clinical biomarkers.

These studies demonstrate that, when equipped with suitable domain-specific knowledge, GP can automatically evolve effective and potentially interpretable feature learning models. While this highlights GP as a highly promising paradigm, research on GP-based feature learning specifically tailored to TSC remains very limited. The unique characteristics of time series data demand specialized program structures and tailored evolutionary search strategies. Accordingly, we develop a new GP method specifically for feature learning in TSC.

\section{Proposed Approach}
\label{s3}
In this study, we focus on feature learning for univariate time series classification. Let $D=\{(\bm{x}_i, y_j)\}_{i=1}^N$ denote a time series dataset, where $N$ is the number of instances, $\bm{x}_i \in \mathbb{R}^L$ is a series of length $L$, and $y_i$ is the corresponding class label.
The proposed GP-based approach aims to automatically evolve a feature learning model $\bm{\phi}(\cdot)$ that maps raw inputs into a discriminative feature space, i.e., $\bm{z}_i=\bm{\phi}(\bm{x}_i)\in\mathbb{R}^{L}$. 
The resulting features aim to highlight task-relevant information, maximizing class separability for a simple downstream classifier $h(\cdot)$ to achieve high generalization performance on unseen data.

\subsection{Algorithm Overview}
\label{s31}
The overall evolutionary process of the proposed GP method is illustrated in Fig. \ref{fig:as1}, with the components newly designed for TSC highlighted in purple. It operates through an iterative loop comprising four main steps until a predefined maximum number of generations $G$ is reached. These four stages are described below.
 \begin{figure}[!t]
 	\centering
 	\includegraphics[width=0.33\textwidth]{figs/Evolutionary_Process.png}
 	\caption{Overall evolutionary process of the proposed GP method.}
 	\label{fig:as1}
 	\vspace{-2mm}
 \end{figure}
 
\subsubsection{\textbf{Population Initialization}}
At this stage, $m$ strongly typed GP trees \cite{stgp} are randomly generated using the ramped half-and-half strategy to initialise a population of $m$ individuals. This procedure combines “full” and “grow” constructions, thereby promoting both structural diversity and functional variety at the start of evolution. Primitives at different layers are sampled from layer-specific terminal or function sets, and every primitive is associated with an explicit input/output type signature. This enforces a predefined ordering of feature learning operations and guarantees that the resulting models are logically valid.

\subsubsection{\textbf{Individual Evaluation}}
Individual evaluation is performed on the training set using $k$-fold cross-validation to encourage generalization of the learned features, given TSC tasks typically having limited labeled data.  Specifically, the training set is transformed according to the evolved individual (i.e. a feature learning model).  The fitness is then defined as the $k$-fold cross-validation result of an extremely randomized trees classifier \cite{geur006extremely} on the transformed training set. Following common practice in the GP-based feature learning community \cite{gpfan}, $k$ is set to $5$.

\subsubsection{\textbf{Parent Selection}}
The parent selection stage identifies high-quality, diverse individuals to ensure that effective building blocks transfer to the next generation. To prevent premature convergence and mitigate the common overfitting problem in TSC tasks, a tailored Pareto tournament selection strategy is employed. This approach is expected to enhance the generalization of the evolved models while preserving the localized competition characteristic of standard tournament selection, thereby maintaining population diversity. Further details of this strategy are provided in Section \ref{s33}.

\subsubsection{\textbf{Offspring Generation}}
The next generation of individuals is produced by applying elitism, crossover, and mutation with predefined probabilities. 
Elitism carries a small number of top-ranked individuals from the current population into the next generation unchanged, avoiding the loss of high-quality solutions. 
Using the selected parents, crossover and mutation are applied to generate the remaining individuals for the next generation. 
Together, these operations balance exploitation of high-quality structures and exploration of new program compositions. 

\subsection{Proposed Multi-layer Program Structure}
\label{s32}
Although many GP methods have been proposed for feature learning in other problems, their program structures are not suited to TSC due to the unique characteristics of time series data. Therefore, this section proposes a new multi-layer program structure specifically designed for TSC. The proposed structure and an evolved model example are illustrated in Fig. \ref{fig:evotsc_program_structure}, and the details of each layer are described below.

\begin{figure*}[!t]
	\centering
	\includegraphics[width=1\textwidth]{figs/EvoTSC_program_structure1.png}
	\vspace{-20pt}
	\caption{Illustration of the proposed multi-layer program structure (a) and an evolved feature learning model example (b).}
	\label{fig:evotsc_program_structure}
\end{figure*}

\subsubsection{\textbf{Segment Detection Layer}}
\label{s321}
The first layer of the proposed structure is an optional segment detection layer, designed to identify an informative segment within a given time series. The segment detection operation is defined as:
\begin{equation}
	\begin{gathered}
		\operatorname{\mathbf{SegDect}}(\bm{x}) = (x_{s_{\text{seg}}}, x_{s_{\text{seg}}+1}, \ldots, x_{s_{\text{\text{seg}}}+\ell_{\text{seg}}}),
	\end{gathered}
\end{equation}
where $\ell_{\text{seg}}$ and $s_{\text{idx}}$ are two terminals for this layer, representing the segment length and the start index, respectively. The evolutionary search optimises their values subject to $1\le \ell_{\text{seg}} < L$ and $1\le s_{\text{seg}}\le L+\ell_{\text{seg}}+1$. 

This layer is designed to provide practitioners with a clear and intuitive entry point for understanding the decision-making process. For example, in clinical electrocardiogram (ECG) analysis, rather than presenting the entire series, the evolved model isolates a specific segment, allowing domain experts to visually verify whether it corresponds to a meaningful physiological event, such as a transient arrhythmia or a specific QRS complex. Similarly, in motion classification, isolating the exact moment of a brief gesture makes the decision logic of the evolved model easy to inspect.

\subsubsection{\textbf{Domain Transform Layer}}
\label{s322}
Unlike many other data modalities, time series can often reveal salient class-discriminative information more explicitly after an appropriate domain transform. 
In the time domain, class differences driven by frequency characteristics may appear only as irregular oscillations. 
In contrast, frequency domain features often reveal these distinctions directly as shifts in the distribution of spectral energy. 
Furthermore, many classification tasks depend primarily on temporal changes rather than absolute values. 
Mapping a series into the difference-domain can highlight discriminative dynamics, such as rapid increases and slow decays, thereby supporting more effective classification. 

Motivated by these observations, the second layer is formulated as a domain transform layer that determines, in a data-driven manner, which domain yields the most informative features for classification. The function set of this layer involves two primitives: a frequency domain transform operator $\operatorname{\mathbf{DomFreq}}(\cdot)$ and a first-order differencing operator $\operatorname{\mathbf{DomDiff}}(\cdot)$. Let $\bm{x}_{\text{in}}=(x_0,x_1,\ldots,x_{\ell_{\text{in}}-1})\in\mathbb{R}^{\ell_{\text{in}}}$ denote the input segment passed from the preceding layer. The function $\operatorname{\mathbf{DomFreq}}(\cdot)$ computes the magnitude spectrum of $\bm{x}_{\text{in}}$ via the discrete fourier transform (DFT):
\begin{equation}
	x'_{u}=\left|\sum_{t=0}^{\ell_{\text{in}}-1} x_{t+1}\exp\!\left(i\,\frac{2\pi}{\ell_{\text{in}}}(u-1)t\right)\right|,
\end{equation}
where $\angle\cdot$ denotes the modulus. $\operatorname{\mathbf{DomDiff}}^2$ computes the first-order differences as:
\begin{equation}
\operatorname{\mathbf{DomDiff}}(\bm{x}_{\text{in}})=(x_2-x_1,\;x_3-x_2,\;\ldots,\;x_{\ell_{\text{in}}}-x_{\ell_{\text{in}}-1}).
\end{equation}
This layer is intentionally optional. When discriminative information is best captured in the time domain, the subsequence produced by the segment detection layer is passed directly to the next layer without applying transform.

\subsubsection{\textbf{Content-adaptive Patching Layer}}
\label{s323}
Patching has recently emerged as an effective technique in time series analysis, where it is initially explored with Transformer architectures \cite{patch}. More recently, several studies have shown that patching can also work well with other backbones, such as CNN and MLP \cite{patch1,patch2}, suggesting that redefining the basic extraction unit from the full series to a set of overlapping patches can enhance feature learning for time series. 

Motivated by these findings, patching is incorporated as an optional layer within the proposed program structure. Given an input segment $\bm{x}_{\text{in}}\in\mathbb{R}^{n_{\text{patch}}}$, this operation segments $\bm{x}_{\text{in}}$ into $n_{\text{stride}}$ overlapping patches with size $\ell_{\text{patch}}$ and stride $s_{\text{patch}}$. The number of patches $n_{\text{patch}}$ is computed as:
\begin{equation}
	n_{\text{patch}} = \left\lfloor \frac{\ell_{\text{in}}+\ell_{\text{patch}}}{s_{\text{patch}}} \right\rfloor + 1.
\end{equation}
A practical challenge of patching is that the optimal patch size can vary substantially across datasets. 
Neural network approaches therefore often require per-dataset tuning to select an appropriate patch size. 
In contrast, the flexibility of GP provides a simple solution: by treating the patch size as a terminal, it can be optimized in a data-driven manner during evolution. 
The search space for $\ell_{\text{patch}}$ is restricted to $\{\lfloor \frac{\ell_{\text{in}}}{2}\rfloor,\lfloor \frac{\ell_{\text{in}}}{4}\rfloor,\ldots,\lfloor \frac{\ell_{\text{in}}}{64}\rfloor\}$. 
Moreover, following common practice in prior study \cite{patch}, the stride is set to $s_{\text{patch}}=\lfloor \frac{\ell_{\text{patch}}}{2}\rfloor$.

\subsubsection{\textbf{Feature Extraction Layer}}
\label{s324}
After patching, the resulting set of $n_{patch}$ patches is passed to the feature extraction layer. This layer defines a set of extraction operators that produce discriminative patch-level features by explicitly capturing two complementary types of information crucial for TSC: shape-related characteristics and statistical distribution properties.

To extract shape information, convolution operations are particularly well-suited, as they measure the similarity between a local pattern and a template specified by a convolution kernel $\bm{w}$. For a processed patch $\bm{p}\in\mathbb{R}^{\ell_{\text{patch}}}$, the 1D convolution operation can be mathematically described as:
\begin{equation}
	\begin{gathered}
		r_j = (\bm{p} * \bm{w})_j = \sum_{i=0}^{c-1} p_{j+i} \cdot w_i, \\
		\text{s.t.} \quad j = 1, 2, \ldots, \ell_{\text{patch}} + c - 1,
	\end{gathered}
\end{equation}
where $\bm{r}$ is the activation map that highlights where and how strongly the pattern occurs within the processed segment, and $c$ is the kernel length.
A distinctive characteristic of time series data is that it can often be viewed as a composition of morphological primitives, such as increasing trends, decreasing trends, and peaks. Based on this observation, prior work \cite{craftkernel} proposes three predefined 1D convolution kernels designed to capture these specific patterns, thereby explicitly encoding shape information. Building upon these three predefined kernels\footnote{Due to space limitations, we omit the detailed formulations here. The explicit definitions of the three convolutional kernels can be found in \cite{craftkernel}.}, this layer defines a set of three corresponding feature extraction operators, denoted as $\mathcal{F}_{\text{shape}} = \{\operatorname{\mathbf{ShapeInc}}, \operatorname{\mathbf{ShapeDec}}, \operatorname{\mathbf{ShapePeak}}\}$, which capture increasing trends, decreasing trends, and peaks, respectively. During the evolutionary search, GP automatically determines which operators $\operatorname{\mathbf{F}}_{\text{shape}} \in \mathcal{F}_{\text{shape}}$ (shape prior) is most discriminative for the processed segment. Once an operator is selected, convolution for the chosen pattern is performed using a set of kernel lengths $\mathcal{C}=\{2^i \mid 2 \le 2^i \le c_{\max}\}$, where $c_{\max} = \lfloor \lambda \cdot \ell_{\text{patch}} \rfloor$ and $\lambda$ is a terminal with the possible values $\{0.25, 0.5, 0.75\}$.
This multi-scale design effectively captures both short-term fluctuations and longer-term trends. In \cite{craftkernel}, these predefined kernels are embedded within a CNN architecture, whereby the semantic clarity of the initial features is obscured by subsequent black-box transformations. To address this limitation, the selected operator $\operatorname{\mathbf{F}}_{\text{shape}}(\cdot)$ defined in this layer directly summarizes each resulting activation map $\bm{r}^{c}$ using three pooling operators, which capture complementary aspects of pattern occurrence:


\begin{align}
	\operatorname{PPV}(\bm{r}^{c}) &=
	\frac{1}{|\bm{r}^{c}|}\sum_{t=1}^{|\bm{r}^{c}|}\mathbb{I}\!\left[r^{c}_t < 0\right],
	\label{eq:ppv_pool}
	\\
	\operatorname{MAX}(\bm{r}^{c}) &= \max\ \bm{r}^{c},
	\label{eq:max_pool}
	\\
	\operatorname{MEAN}(\bm{r}^{c}) &= \frac{1}{|\bm{r}^{c}|}\sum_{t=1}^{|\bm{r}^{c}|} r^{c}_t,
\end{align}
where $\mathbb{I}[\cdot]$ is the indicator function. $\operatorname{PPV}$ measures the frequency of activations, $\operatorname{MAX}$ captures the strongest match, and $\operatorname{MEAN}$ reflects the overall response intensity. Finally, the layer outputs a feature vector by concatenating pool descriptors across all kernel lengths:
\begin{equation}
	\operatorname{\mathbf{F}}_{\text{shape}}(\bm{p})
	=
	\bigoplus_{c\in\mathcal{C}}
	\Big(
	\operatorname{PPV}(\bm{r}^{c}),\;
	\operatorname{MAX}(\bm{r}^{c}),\;
	\operatorname{MEAN}(\bm{r}^{c})
	\Big),
\end{equation}
where $\oplus$ denotes vector concatenation. This yields features that are effective for classification while maintaining semantic clarity.

Beyond shape-related information, classes can also differ in the statistical distribution of the observed values. Classic summary statistics, such as the minimum, maximum, and median, provide simple and interpretable descriptors of a distribution. These statistics motivate a broader view: rather than extracting only a small set of fixed features, a discriminative feature can be constructed by sampling the empirical quantile function more densely, which captures the overall distribution profile of a segment. To capture this information, this layer defines a extraction operator for statistical distribution feature, denoted as $\operatorname{\mathbf{StatisDist}}(\cdot)$. Given a processed patch $\bm{p}\in\mathbb{R}^{\ell_{\text{patch}}}$, its values are treated as an empirical sample from an unknown distribution. To form a distributional encoding, the values of $\bm{p}$ are sorted in ascending order to obtain the order statistics $\bm{p}^{\uparrow} = (p^{\uparrow}_1, p^{\uparrow}_2, \ldots, p^{\uparrow}_{\ell_{\text{patch}}})$. The sorted sequence is then uniformly subsampled to retain a proportion $\tau$ of the points ($M=\lfloor \tau \times \ell_{\text{patch}} \rfloor$), where $\tau$ is a terminal with the possible values $\{0.25, 0.5, 0.75\}$, allowing GP to automatically select the sampling density in a data-driven manner. Let the selected indices be:
\begin{equation}
	idx_j = 1 + \mathrm{round}\!\left(\frac{(\ell_{\text{patch}}-1)\,j}{M+1}\right), \quad j=0,\ldots,M-1,
\end{equation}
and this operator can be defined as:
\begin{equation}
	\operatorname{\mathbf{StatisDist}}(\bm{p}) = \big[p^{\uparrow}_{idx_0},\,p^{\uparrow}_{idx_1},\,\ldots,\,p^{\uparrow}_{idx_{M-1}}\big].
\end{equation}

Ultimately, evolutionary search selects a suitable extraction operator $\mathbf{F} \in \{\mathbf{ShapeInc}, \allowbreak \mathbf{ShapeDec}, \allowbreak \mathbf{ShapePeak}, \allowbreak \mathbf{StatisDist}\}$. This selected operator is then applied identically and independently to all $n_{patch}$ patches. This shared application ensures that localized discriminative information can be captured regardless of where it occurs in the segment. Finally, the layer outputs the feature vector by concatenating the extraction results of all patches:
\begin{equation}
	\bm{z} = \bigoplus_{i=1}^{n_{patch}} \operatorname{\mathbf{F}}(\bm{p}_i).
\end{equation}

\subsubsection{\textbf{Feature Concatenation Layer}}
\label{s325}
While the preceding layers learn discriminative  features from specific segments or domains, a single learned feature vector branch may be insufficient for complex TSC tasks. 
Therefore, this final layer concatenates multiple feature vectors.

To support flexible multi-branch composition, this layer provides two categories of functions. 
The first category includes the base functions $\operatorname{\mathbf{FeaCon2}}$, $\operatorname{\mathbf{FeaCon3}}$, and $\operatorname{\mathbf{FeaCon4}}$, which concatenate two, three, or four feature vectors into a single output, respectively. 
The second category, $\operatorname{\mathbf{FeaConH}}$, concatenates a feature vector with the output of $\operatorname{\mathbf{FeaCon2}}$, $\operatorname{\mathbf{FeaCon3}}$, or $\operatorname{\mathbf{FeaCon4}}$.

To provide a clear overview of the program structure, the function and terminal sets of the proposed multi-layer program structure are summarized in Table \ref{tab:function_set} and Table \ref{tab:terminal_set}. The proposed multi-layer structure thoroughly explores the inherent advantages of GP by naturally embedding diverse forms of prior expert knowledge into the feature learning process. By doing so, the search space is purposefully biased toward operations known to be effective for TSC tasks. Ultimately, the evolutionary process aims to dynamically select and compose appropriate expert components from a unified search space according to the characteristics of the input data.

\begin{table}[htbp]
	\centering
	\caption{Function Set of the Proposed Multi-layer Program Structure.}
	\label{tab:function_set}
	\resizebox{\columnwidth}{!}{%
		\begin{tabular}{@{}llll@{}}
			\toprule
			\textbf{Layer} & \textbf{Function} & \textbf{Input Type} & \textbf{Output Type} \\
			\midrule
			Segment Detection & $\operatorname{\mathbf{SegDect}}$ & Series, $\ell_{\text{seg}}$, $s_{\text{seg}}$ & Segment \\
			\midrule
			\multirow{2}{*}{Domain Transform} & $\operatorname{\mathbf{DomFreq}}$ & Series/Segment & Segment \\
			& $\operatorname{\mathbf{DomDiff}}$ & Series/Segment & Segment \\
			\midrule
			\makecell[l]{Content-adaptive\\Patching} & $\operatorname{\mathbf{AdaPatch}}$ & Series/Segment, $\ell_{\text{patch}}$ & Patches \\
			\midrule
			\multirow{4}{*}{\makecell[l]{Feature\\Extraction}} & $\operatorname{\mathbf{ShapeInc}}$ & Series/Segment/Patches, $\lambda$ & Vector \\
			& $\operatorname{\mathbf{ShapeDec}}$ &  Series/Segment/Patches, $\lambda$ & Vector \\
			& $\operatorname{\mathbf{ShapePeak}}$ &  Series/Segment/Patches, $\lambda$ & Vector \\
			& $\operatorname{\mathbf{StatisDist}}$ &  Series/Segment/Patches, $\tau$ & Vector \\
			\midrule
			\multirow{4}{*}{\makecell[l]{Feature\\Concatenation}} & $\operatorname{\mathbf{FeaCon2}}$ & 2 Vector & Vectors \\
			& $\operatorname{\mathbf{FeaCon3}}$ & 3 Vector & Vectors \\
			& $\operatorname{\mathbf{FeaCon4}}$ & 4 Vector & Vectors \\
			& $\operatorname{\mathbf{FeaConH}}$ & Vector, Vectors & Vectors \\
			\bottomrule
		\end{tabular}%
	}
\end{table}

\begin{table}[htbp]
	\centering
	\caption{Terminal Set of the Proposed Multi-layer Program Structure.}
	\label{tab:terminal_set}
	\resizebox{\columnwidth}{!}{%
		\begin{tabular}{@{}lll@{}}
			\toprule
			\textbf{Layer} & \textbf{Terminal} & \textbf{Search Range} \\
			\midrule
			\multirow{2}{*}{Segment Detection} & $\ell_{\text{seg}}$ & $\{1, 2, \ldots, L-1\}$ \\
			& $s_{\text{seg}}$ & $\{1, 2, \ldots, L-\ell_{\text{seg}}+1\}$ \\
			\midrule
			\makecell[l]{Content-adaptive\\Patching} & $\ell_{\text{patch}}$ & $\left\{\left\lfloor \frac{\ell_{\text{in}}}{2}\right\rfloor, \left\lfloor \frac{\ell_{\text{in}}}{4}\right\rfloor, \ldots, \left\lfloor \frac{\ell_{\text{in}}}{64}\right\rfloor\right\}$ \\
			\midrule
			\multirow{2}{*}{Feature Extraction} & $\tau$ & $\{0.25, 0.5, 0.75\}$ \\
			& $\lambda$ & $\{0.25, 0.5, 0.75\}$ \\
			\bottomrule
		\end{tabular}%
	}
\end{table}

\subsection{Parent Selection Strategy}
\label{s33}
Tournament selection used in previous GP-based feature learning methods \cite{bitevc,wangtevc,tevc0} typically relies on  the fitness value, i.e. the averaged
accuracy of $k$-fold cross-validation,  as the selection criterion. However, this scalar metric obscures performance variance across different data splits. It cannot distinguish between individuals that generalize consistently across all folds and those that achieve high accuracy on only a small number of folds while performing poorly on the others. By failing to penalize such instability, it may misdirect the evolutionary process toward models that overfit to specific data splits, resulting in features with poor generalization ability. To address this issue, a tailored Pareto tournament selection strategy \cite{paretotournament} is proposed.

Unlike standard Pareto tournament selection, which typically uses performance and model size as dual objectives, the proposed strategy treats the accuracy on each fold as an independent optimization objective. 
Specifically, the selection criterion is defined as a multi-objective vector:
\begin{equation}
	\bm{V}(\bm{\phi}) = \big( \operatorname{acc}_1(\bm{\phi}), \operatorname{acc}_2(\bm{\phi}), \ldots, \operatorname{acc}_k(\bm{\phi}) \big),
\end{equation}
where $\operatorname{acc}_j(\bm{\phi})$ denotes the classification accuracy on the $j$-th fold during the cross-validation on the training set during fitness evaluation.
During each selection event, a tournament is formed by randomly sampling $\mu\%$ of the population. 
This design retains the localized competition property of standard tournament selection, which helps preserve population diversity. Within this sampled subset, individuals are compared using Pareto dominance. 
An individual $\bm{\phi}_A$ is said to dominate $\bm{\phi}_B$ if and only if it performs no worse than $\bm{\phi}_B$ across all $k$ folds and performs strictly better on at least one fold. Unlike standard tournament selection, which selects only a single winner per event, the proposed strategy leverages this dominance relation to select the local non-dominated set from the tournament. All individuals within this non-dominated set are then added to the parent pool, and the tournament process is repeated until the required number of parents is obtained. The complete procedure of the tailored Pareto tournament selection is summarized in Algorithm~\ref{alg:pareto_tournament}. 

By enforcing Pareto dominance across all data splits, the selection mechanism rigorously filters out fragile individuals. A candidate can no longer survive the tournament merely by achieving an exceptionally high accuracy on a single fold if it compromises performance on the others. Thus it creates evolutionary pressure that explicitly favors feature learning models capable of learning universally stable features across multiple data subsets. To the best of our knowledge, this is the first attempt to address the overfitting challenge in TSC from an evolutionary perspective. The proposed strategy embeds an inductive bias toward generalization directly into the evolution process, demonstrating the unique value of exploring evolutionary machine learning.
\begin{algorithm}[t]
	\caption{Tailored Pareto Tournament Parent Selection}
	\label{alg:pareto_tournament}
	\small
	\begin{algorithmic}[1]
		\Require Population $\mathcal{P}$, tournament ratio $\mu$, number of folds $k$, required number of parents $N_p$
		\Ensure Parent pool $\mathcal{M}$
		
		\State $\mathcal{M} \gets \emptyset$
		\State $n_t \gets \lceil \mu |\mathcal{P}| \rceil$
		
		\While{$|\mathcal{M}| < N_p$}
		\State Randomly sample a tournament set $\mathcal{T} \subseteq \mathcal{P}$ with $|\mathcal{T}| = n_t$
		\State $\mathcal{ND} \gets \emptyset$
		\ForAll{$\bm{\phi}_i \in \mathcal{T}$}
		\State dominated $\gets$ \textbf{false}
		\ForAll{$\bm{\phi}_j \in \mathcal{T}, \bm{\phi}_j \neq \bm{\phi}_i$}
		\If{$\bm{\phi}_j \succ \bm{\phi}_i$}
		\State dominated $\gets$ \textbf{true}
		\State \textbf{break}
		\EndIf
		\EndFor
		\If{not dominated}
		\State $\mathcal{ND} \gets \mathcal{ND} \cup \{\bm{\phi}_i\}$
		\EndIf
		\EndFor
		\State $\mathcal{M} \gets \mathcal{M} \cup \mathcal{ND}$
		\EndWhile
		
		\State \Return first $N_p$ individuals in $\mathcal{M}$
	\end{algorithmic}
\end{algorithm}

\section{Experiment Design}
\label{s4}
\subsection{Datasets}
\label{s41}
Rather than relying on additional resampling or imputation procedures that may introduce confounding factors, we focus on datasets whose time series are equal-length and free of missing values. Accordingly, the experiments are conducted on 86 time series datasets from the UCR Time Series Classification Archive \cite{UCRArchive2018}. A detailed summary of these datasets is provided in the supplementary material. The total number of instances per dataset ranges from 40 to 5{,}000. The original train/test splits provided by the archive are adopted throughout the experiments.

These datasets exhibit considerable diversity in their intrinsic characteristics: the number of classes ranges from 2 to 60, and the time series length varies from 15 to 2{,}800. Moreover, they are collected from a broad spectrum of application scenarios, including biomedical (10), industrial (21), motion (17), image outline (20), spectral (11) and simulated (7), providing a comprehensive testbed for evaluating the effectiveness of the learned features.

\subsection{Comparison Methods}
\label{s42}
This section describes the comparison methods used in the experiments, covering eleven methods across four categories. The details of each method are presented below.

\subsubsection{Common Machine Learning Methods}
Five commonly used machine learning classifiers are used, including $k$-nearest neighbor ($k$-NN), support vector machine (SVM), logistic regression (LR), random forest (RF), and extremely randomized trees (ET). These classifiers are selected because they are widely used and represent different learning mechanisms, covering linear, distance-based, and tree-based classification paradigms.

\subsubsection{Hand-crafted Feature Extraction Methods}
As a representative hand-crafted feature extraction method, catch22 \cite{catch22} is included as a comparison method. It summarizes each time series using a compact set of 22 minimally redundant features designed to capture diverse data properties, such as distributional characteristics, temporal dependence, and fluctuation patterns.

\subsubsection{Neural Network-based Methods}
Two neural network-based methods are selected for comparison in our experiments. TS2Vec \cite{ts2vec}, employs a hierarchical contrastive learning framework to contrast augmented context views across multiple temporal resolutions. SoftCLT \cite{softclt}, refines the traditional contrastive learning paradigm by replacing hard positive and negative assignments with soft pairwise weights. These two models are chosen because they are state-of-the-art NN-based approaches for TSC, and thus provide strong baselines for evaluating the performance of proposed method.

\subsubsection{Foundation Model-based Methods}
Three foundation model-based methods are employed in our experiments. MOMENT \cite{moment} is a model for general-purpose time series analysis, and its largest version with 300 million parameters is adopted in our experiments\footnote{\url{https://huggingface.co/AutonLab/MOMENT-1-large}}. Mantis \cite{mantis} is a lightweight TSFM with 8 million parameters specifically designed for classification tasks, pre-trained via contrastive learning on seven million time series instances\footnote{\url{https://huggingface.co/paris-noah/Mantis-8M}}. TiViT \cite{tivit} adopts a cross-modality strategy to leverage the representational power of a large-scale vision Transformer with one billion parameters pre-trained on natural images\footnote{\url{https://huggingface.co/laion/CLIP-ViT-H-14-laion2B-s32B-b79K}}. These three methods are selected as they represent diverse paradigms in the rapidly emerging area of time series foundation models, offering a modern benchmark.

\subsection{Parameter Settings}
\label{s43}
\subsubsection{Proposed GP Method}
Following the common practice in GP-based feature learning methods \cite{wutevc}, the parameter settings of proposed EvoTSC method are shown in Table \ref{tab:gp_params}. The minimum tree depth is set to 2, corresponding to the minimal model that employs only the feature extraction and feature concatenation layers as fixed components. The maximum tree depth is set to 6, corresponding to the maximal model that activates all layers and utilizes $\operatorname{\mathbf{FeaConH}}$ for feature concatenation. Moreover, since fitness evaluation in GP mainly provides a relative ranking signal for comparing candidate feature learning models rather than a precise estimate of absolute performance differences \cite{9656554,10783045}, a lightweight classifier is sufficient for this purpose. Based on preliminary experiments, an extremely randomized trees classifier with 10 trees is adopted, as it achieves a good balance between evaluation efficiency and ranking reliability.

\begin{table}[t]
	\centering
	\caption{Parameter Settings of the Proposed Method.}
	\label{tab:gp_params}
	\renewcommand{\arraystretch}{1.15}
	\begin{tabular}{c c}
		\hline
		\textbf{Parameter} & \textbf{Value} \\
		\hline
		Population size & 100 \\
		Maximal number of generations & 50 \\
		Crossover and mutation rates & 0.8 and 0.19 \\
		Elitism rate & 0.01 \\
		Minimum tree depth & 2 \\
		Maximum tree depth & 6 \\
		\hline
	\end{tabular}
\end{table}

\subsubsection{Existing Methods}
For the five common machine learning classifiers, the number of neighbors for $k$-NN is set to 1, following common practice in TSC, while the other classifiers use their default settings. For the neural network-based methods, the recommended hyperparameter settings provided in their papers and official open-source implementations are adopted. For the foundation model-based methods, all experiments use the pre-trained models released by the authors on Hugging Face, with the original model configurations kept unchanged.

\section{Results and Analysis}
\label{s5}
\subsection{Effectiveness of the Learned Features}
\label{s51}
In this section, the effectiveness of the learned features is investigated by comparing the performance of common ML classifiers applied directly to raw time series data against their performance when coupled with the evolved feature learning models. All experiments are independently repeated 30 times. To determine whether the performance differences are statistically significant, a Wilcoxon rank-sum test at a significance level of $\alpha = 0.05$ is conducted on each dataset. The results are summarized as win/tie/loss (W/T/L) counts, representing the number of datasets where EvoTSC performs significantly better than, comparably to, or significantly worse than the raw data baseline.

As shown in Fig.~\ref{fig:effectiveness}, the W/T/L counts are annotated at the top of each box plot. Each box plot visualizes the distribution of average accuracy improvements over the raw data baseline across all datasets. The red dashed line at $y=0$ serves as the reference: values above this line indicate that the learned features improve classification accuracy, while values below indicate degradation.

Across all five classifiers, the W/T/L counts indicate that the features learned by EvoTSC significantly outperform or match the raw data on over 70\% of the datasets. Moreover, a number of positive outliers can be observed, indicating that on certain datasets the learned features bring particularly notable performance improvement. While a small number of negative outliers also exist, they are considerably fewer.
\begin{figure}
	\centering
	\includegraphics[width=\columnwidth]{figs/accuracy_difference_boxplot.png}
	\vspace{-20pt}
	\caption{Distribution of accuracy improvement over the raw data baseline across all datasets.}
	\label{fig:effectiveness}
\end{figure}

\subsection{Comparisons with Existing TSC Methods}
\label{s52}
This section evaluates the proposed method through comparisons with six advanced TSC approaches. EvoTSC uses the ET classifier, as it yields the highest number of datasets with significant improvement or comparable performance. For TS2Vec, SoftCLT, MOMENT, Mantis, and TiViT, the classifiers and protocols recommended in their respective original papers are employed. Since catch22 does not specify a recommended classifier, the same ET classifier as EvoTSC is used. Similarly to last section, all experiments are independently repeated 30 times, and a Wilcoxon rank-sum test at a significance level of $\alpha = 0.05$ is used to assess statistical significance.

The experimental results are presented in Table~\ref{tab:pairwise_sig}, where each cell denotes the number of datasets on which the row method statistically outperforms ($+$), performs comparably to ($\sim$), or underperforms ($-$) the column method. Three key observations can be drawn from the results.
First, compared with the hand-crafted feature extraction approach catch22, EvoTSC achieves an overwhelming advantage, winning on 71 datasets and losing on only 6. This substantial margin confirms that the feature learning models evolved by EvoTSC are far more expressive and adaptive than a fixed set of feature extractors. Second, compared with the NN-based approaches SoftCLT and TS2Vec, EvoTSC continues to demonstrate superior performance, winning on 42 and 43 datasets, respectively. This suggests that EvoTSC can evolve feature learning models more effective than these advanced NN-based feature learning methods. Third, a noteworthy finding emerges from the comparison with recent TSFM (Mantis, MOMENT, and TiViT). Despite leveraging hundreds of millions or even billions of parameters pre-trained on vast amounts of external data, these foundation models are consistently outperformed by EvoTSC. Interestingly, they also fail to surpass the domain-specific NN-based approaches (SoftCLT and TS2Vec) in the pairwise comparisons. This observation highlights a critical limitation of current foundation models for TSC: while large-scale pre-training may capture general temporal patterns, the resulting out-of-the-box representations are often misaligned with the specific discriminative features required by diverse downstream TSC tasks. Although fine-tuning these foundation models on target datasets may potentially bridge this gap, doing so demands substantial computational resources. Notably, even the paper of TiViT does not attempt such fine-tuning due to the prohibitive cost \cite{tivit}.
\begin{table*}[ht]
	\centering
	\caption{Pairwise Wilcoxon Rank-Sum Test Results ($p < 0.05$) among Seven Methods across All Datasets.}
	\label{tab:pairwise_sig}
		\begin{tabular}{l cccccc}
			\toprule
			\textbf{Method} & \textbf{TiViT} & \textbf{Mantis} & \textbf{MOMENT} & \textbf{SoftCLT} & \textbf{TS2Vec} & \textbf{catch22} \\
			\midrule
			\textbf{EvoTSC}  & 49(+)/9($\sim$)/28(-)  & 57(+)/15($\sim$)/14(-) & 57(+)/15($\sim$)/14(-) & 42(+)/18($\sim$)/26(-) & 43(+)/15($\sim$)/28(-) & 71(+)/9($\sim$)/6(-)  \\
			\textbf{TiViT}   & -                       & 57(+)/6($\sim$)/23(-)  & 62(+)/4($\sim$)/20(-)  & 36(+)/8($\sim$)/42(-)  & 36(+)/12($\sim$)/38(-) & 58(+)/7($\sim$)/21(-) \\
			\textbf{Mantis}  & -                       & -                       & 43(+)/4($\sim$)/39(-)  & 21(+)/13($\sim$)/52(-) & 21(+)/10($\sim$)/55(-) & 49(+)/8($\sim$)/29(-) \\
			\textbf{MOMENT}  & -                       & -                       & -                       & 21(+)/9($\sim$)/56(-)  & 25(+)/10($\sim$)/51(-) & 50(+)/8($\sim$)/28(-) \\
			\textbf{SoftCLT} & -                       & -                       & -                       & -                       & 30(+)/37($\sim$)/19(-) & 64(+)/6($\sim$)/16(-) \\
			\textbf{TS2Vec}  & -                       & -                       & -                       & -                       & -                       & 61(+)/9($\sim$)/16(-) \\
			\bottomrule
		\end{tabular}
\end{table*}

Furthermore, to rule out the possibility that the superior performance of EvoTSC is attributable to the choice of the ET classifier rather than the effectiveness of evolved feature learning models, an additional experiment is conducted in which all comparison methods (excluding catch22, which already uses ET) use the same ET classifier. The results presented in Table~\ref{tab:pairwise_et} show that EvoTSC continues to outperform all comparison methods under this unified classifier setting.
\begin{table*}[ht]
	\centering
	\caption{Pairwise Wilcoxon Rank-Sum Test Results ($p < 0.05$) Under a Unified ET Classifier across All Datasets.}
	\label{tab:pairwise_et}
	\renewcommand{\arraystretch}{1.15}
	\setlength{\tabcolsep}{6pt}
	\begin{tabular}{lccccc}
		\toprule
		\textbf{Method} & \textbf{TiViT\_ET} & \textbf{Mantis\_ET} & \textbf{MOMENT\_ET} & \textbf{SoftCLT\_ET} & \textbf{TS2Vec\_ET} \\
		\midrule
		\textbf{EvoTSC}      & 52(+)/15($\sim$)/19(-) & 53(+)/15($\sim$)/18(-) & 68(+)/11($\sim$)/7(-)  & 57(+)/15($\sim$)/14(-) & 54(+)/19($\sim$)/13(-) \\
		\textbf{TiViT\_ET}   & --                      & 42(+)/11($\sim$)/33(-) & 63(+)/6($\sim$)/17(-)  & 39(+)/8($\sim$)/39(-)  & 40(+)/6($\sim$)/40(-)  \\
		\textbf{Mantis\_ET}  & --                      & --                      & 51(+)/7($\sim$)/28(-)  & 31(+)/12($\sim$)/43(-) & 33(+)/14($\sim$)/39(-) \\
		\textbf{MOMENT\_ET}  & --                      & --                      & --                      & 18(+)/10($\sim$)/58(-) & 21(+)/13($\sim$)/52(-) \\
		\textbf{SoftCLT\_ET} & --                      & --                      & --                      & --                      & 28(+)/45($\sim$)/13(-) \\
		\bottomrule
	\end{tabular}
\end{table*}

To provide a more comprehensive and intuitive comparison across all approaches, we further conduct a critical difference (CD) analysis \cite{JMLRCD} over proposed EvoTSC method, all comparison methods in Section \ref{s52} (with both original and unified ET classifiers), and the five baseline classifiers trained directly on raw data in Section \ref{s51}.
Specifically, on each dataset we rank all methods by classification accuracy, compute the average rank across datasets, and then apply the Friedman test followed by the Nemenyi
post-hoc procedure at $\alpha=0.05$ to obtain the CD diagram. As shown in Fig.~\ref{fig:cd_diagram}, the resulting diagram has $CD=2.663$. EvoTSC achieves the best average rank of $4.872$, indicating the strongest overall performance. It is statistically comparable to the top-performing four baselines within the same non-significant clique (SoftCLT, TS2Vec, TiViT, and SoftCLT\_ET), while significantly outperforming the remaining seven methods
whose average ranks differ from EvoTSC by more than the $CD$.
\begin{figure}[ht]
	\centering
	\includegraphics[width=0.49\textwidth]{figs/cd_diagram.png}
	\vspace{-20pt}
	\caption{Critical difference diagram of average ranks over all datasets. Lower rank is better.}
	\label{fig:cd_diagram}
\end{figure}

\subsection{Grouped Dataset Analysis}
\label{s53}
This section further investigates the performance of the proposed EvoTSC method across varying data characteristics through a group-wise analysis. The datasets are partitioned based on three key properties: the number of classes (four groups), time series length (four groups), and dataset type (six groups)\footnote{Detailed information regarding these properties for each dataset is provided in the supplementary material.}. For each of the 14 resulting groups, the average rank of every method is computed across its constituent datasets. The results are summarized in Table~\ref{tab:grouped}.
\begin{table*}[ht]
	\centering
	\footnotesize
	\setlength{\tabcolsep}{3.0pt}
	\renewcommand{\arraystretch}{1.15}
	\caption{Average rank of each method within fourteen dataset groups. The best rank in each row is in \textbf{bold} and the second best is \underline{underlined}. $n$ denotes the number of datasets in each group.}
	\label{tab:grouped}
	\resizebox{\textwidth}{!}{%
		\begin{tabular}{llccccccccccccccccc}
			\toprule
			\multirow{2}{*}{Criterion} & \multirow{2}{*}{Group} &
			\multicolumn{17}{c}{Average rank} \\
			\cmidrule(lr){3-19}
			& &
			$k$-NN & SVM & LR & RF & ET & catch22 &
			TS2Vec\_ET & SoftCLT\_ET & MOMENT\_ET & Mantis\_ET & TiViT\_ET &
			TS2Vec & SoftCLT & MOMENT & Mantis & TiViT & \textsc{EvoTSC} \\
			\midrule
			\multirow{4}{*}{Classes $C$}
			& $C=2$ ($n=30$)
			& 13.650 & 10.667 & 12.717 & 11.633 & 10.633 & 10.550
			& 7.517 & 6.783 & 10.383 & 8.433 & 8.450
			& 6.150 & \textbf{5.533} & 8.467 & 9.283 & 6.183 & \underline{5.967} \\
			& $3\leq C\leq5$ ($n=27$)
			& 13.796 & 9.778 & 11.870 & 10.481 & 10.426 & 10.852
			& 9.444 & 8.685 & 10.315 & 8.537 & 7.352
			& 7.333 & \underline{5.852} & 7.981 & 8.704 & 6.778 & \textbf{4.815} \\
			& $6\leq C\leq10$ ($n=15$)
			& 15.633 & 10.200 & 15.933 & 11.400 & 8.867 & 10.000
			& 7.733 & 6.600 & 11.667 & 9.133 & 6.200
			& \underline{5.733} & \underline{5.733} & 8.100 & 10.333 & 6.133 & \textbf{3.600} \\
			& $C>10$ ($n=14$)
			& 14.357 & 11.750 & 15.821 & 13.000 & 11.357 & 10.857
			& 6.429 & 6.286 & 11.714 & 6.000 & 8.821
			& \underline{4.286} & \textbf{4.071} & 10.429 & 8.250 & 5.500 & \textbf{4.071} \\
			\midrule
			\multirow{4}{*}{Length $L$}
			& $L\leq150$ ($n=31$)
			& 14.532 & 9.839 & 13.032 & 9.726 & 8.258 & 11.774
			& 7.516 & 6.871 & 11.500 & 8.919 & 8.323
			& 6.065 & \underline{5.145} & 8.855 & 9.645 & 8.097 & \textbf{4.903} \\
			& $151\leq L\leq500$ ($n=22$)
			& 13.955 & 11.205 & 13.432 & 12.659 & 10.795 & 12.682
			& 8.932 & 7.386 & 10.000 & 8.205 & 8.000
			& 5.545 & \textbf{4.477} & 6.045 & 9.182 & \underline{5.205} & 5.295 \\
			& $501\leq L\leq1000$ ($n=16$)
			& 14.031 & 11.219 & 13.531 & 11.688 & 12.062 & 8.844
			& 8.062 & 7.969 & 10.281 & 6.719 & 7.000
			& 7.281 & 6.656 & 9.719 & 7.156 & \textbf{5.000} & \underline{5.781} \\
			& $L>1000$ ($n=17$)
			& 13.853 & 10.029 & 14.500 & 12.824 & 12.118 & 7.412
			& 7.529 & 7.176 & 11.059 & 8.235 & 7.206
			& 6.000 & 6.029 & 10.235 & 9.912 & \underline{5.412} & \textbf{3.471} \\
			\midrule
			\multirow{6}{*}{Type}
			& Biomedical ($n=10$)
			& 12.150 & 10.400 & 13.000 & 12.850 & 10.750 & 8.200
			& 5.350 & 6.550 & 13.000 & 7.450 & 9.050
			& 5.750 & \underline{5.050} & 11.650 & 9.100 & 7.950 & \textbf{4.750} \\
			& Industrial ($n=21$)
			& 13.905 & 11.429 & 13.643 & 11.310 & 10.595 & 8.214
			& 7.881 & 7.429 & 11.310 & 8.714 & 7.786
			& 6.786 & 6.047 & 9.476 & 9.429 & \underline{4.714} & \textbf{4.333} \\
			& Motion ($n=17$)
			& 14.324 & 12.941 & 15.412 & 13.647 & 11.412 & 11.176
			& 8.029 & 7.000 & 9.647 & 6.118 & \underline{5.588}
			& 5.706 & 5.912 & 8.029 & 7.824 & \textbf{4.441} & 5.794 \\
			& ImageOutline ($n=20$)
			& 15.225 & 9.450 & 14.350 & 10.200 & 8.950 & 12.850
			& 8.850 & 7.050 & 10.050 & 8.475 & 7.500
			& 6.200 & \underline{5.150} & 6.800 & 8.875 & 8.225 & \textbf{4.800} \\
			& Spectral ($n=11$)
			& 13.227 & 5.909 & 7.682 & 9.591 & 11.136 & 11.727
			& 9.955 & 8.864 & 9.591 & 11.182 & 11.455
			& 6.409 & \underline{4.909} & 7.182 & 10.773 & 8.909 & \textbf{4.500} \\
			& Simulated ($n=7$)
			& 15.786 & 11.929 & 16.071 & 11.071 & 9.571 & 11.571
			& 6.357 & 6.571 & 13.000 & 7.214 & 6.214
			& 5.286 & \underline{4.571} & 10.000 & 9.429 & \textbf{3.000} & 5.357 \\
			\bottomrule
	\end{tabular}}
\end{table*}

\subsubsection{Effect of the Number of Classes}
The upper panel of Table~\ref{tab:grouped} partitions the datasets by the number of classes. When the number of classes is small ($C\!=\!2$), SoftCLT achieves the best average rank of 5.533, with EvoTSC closely following in second place at 5.967. As the number of classes increases, EvoTSC demonstrates a clear advantage: it achieves the best rank in the $3 \!\leq\! C \!\leq\! 5$ group (4.815) and the $6 \!\leq\! C \!\leq\! 10$ group (3.600), exceeding the second-placed method by more than one rank on average. In the many-class group ($C\!>\!10$), EvoTSC and SoftCLT are tied at the best rank of 4.071, followed closely by TS2Vec at 4.286. These three methods consistently occupy the top two ranks across all class-count groups. 

\subsubsection{Effect of Time Series Length}
The middle panel of Table~\ref{tab:grouped} groups the datasets by time series length. EvoTSC achieves two best and one second-best average ranks across the four groups. Its rank of 3.471 on series exceeding length 1000 is the lowest observed in the entire table, revealing a pronounced advantage on long time series. This can be attributed to the inherent flexibility of GP, which enables the production of a sufficiently rich feature set to capture the complex discriminative patterns embedded in long series.

\subsubsection{Effect of the Dataset Type}
The lower panel of Table~\ref{tab:grouped} groups the datasets by application type. EvoTSC achieves the best average rank in four of the six types. For Motion datasets, TiViT achieves the best rank (4.441), which is consistent with its design: by converting time series into images and exploiting vision Transformer, it is naturally well suited to data characterized by action or trajectory related local pattern changes. Similarly, TiViT ranks first on Simulated datasets (3.000), because many UCR simulated problems are built around embedded shape patterns. By contrast, TiViT ranks only 8.225 on ImageOutline datasets. A possible explanation is that these datasets are already one-dimensional encodings of object outline, so transforming them again into images may provide less additional benefit than methods that operate directly on the original 1D shape signal.

Overall, EvoTSC ranks within the top two among all seventeen methods in 11/14 groups. These results demonstrate that EvoTSC is capable of evolving effective feature learning models for datasets with diverse properties, highlighting its strong adaptability across various TSC scenarios.

\section{Further Analysis}
\label{s6}
\subsection{Ablation Studies}
\label{s61}
To investigate the contribution of each component in the proposed EvoTSC method, a comprehensive ablation study is conducted by systematically disabling individual components to produce degraded variants. Specifically, the ablation is organized from three perspectives, yielding nine degraded versions in total. Following the same grouped dataset analysis protocol as in Section~\ref{s53}, the average rank of each variant is computed within each dataset group. The results are reported in Table~\ref{tab:ablation}. 
\begin{table*}
	\centering
	\footnotesize
	\setlength{\tabcolsep}{3.0pt}
	\caption{Average rank of each ablation variant within fourteen dataset groups. The best rank in each row is in \textbf{bold} and the second best is \underline{underlined}. $n$ denotes the number of datasets in each group.}
	\label{tab:ablation}
	\resizebox{\textwidth}{!}{%
		\begin{tabular}{llcccccccccc}
			\toprule
			\multirow{2}{*}{Criterion} & \multirow{2}{*}{Group} &
			\multicolumn{10}{c}{Average rank} \\
			\cmidrule(lr){3-12}
			& &
			ShapeInc & ShapeDec & ShapePeak & StatisDist & AllFea &
			wo\_Dom & wo\_Patch & wo\_Con & wo\_Pareto & \textsc{EvoTSC} \\
			\midrule
			\multirow{4}{*}{Classes $C$}
			& $C=2$ ($n=30$)
			& 7.933 & 8.067 & 6.567 & 7.717 & 5.183
			& 4.150 & 4.200 & 4.867 & \underline{3.633} & \textbf{2.683} \\
			& $3\leq C\leq5$ ($n=27$)
			& 8.370 & 8.130 & 6.704 & 8.019 & 6.222
			& 3.741 & 4.204 & 4.148 & \underline{2.759} & \textbf{2.704} \\
			& $6\leq C\leq10$ ($n=15$)
			& 7.400 & 8.067 & 8.200 & 8.467 & 5.733
			& 3.700 & 3.900 & 5.000 & \textbf{2.200} & \underline{2.333} \\
			& $C>10$ ($n=14$)
			& 8.929 & 8.786 & 7.571 & 8.357 & 5.071
			& 3.429 & 3.357 & 5.000 & \underline{2.357} & \textbf{2.143} \\
			\midrule
			\multirow{4}{*}{Length $L$}
			& $L\leq150$ ($n=31$)
			& 8.290 & 8.258 & 7.516 & 7.758 & 4.790
			& 3.823 & 4.532 & 4.613 & \underline{2.887} & \textbf{2.532} \\
			& $151\leq L\leq500$ ($n=22$)
			& 8.636 & 8.114 & 6.295 & 8.818 & 6.091
			& 3.295 & 4.250 & 4.545 & \underline{2.682} & \textbf{2.273} \\
			& $501\leq L\leq1000$ ($n=16$)
			& 7.000 & 7.875 & 6.406 & 7.656 & 5.938
			& 4.875 & \underline{3.406} & 5.125 & 3.656 & \textbf{3.062} \\
			& $L>1000$ ($n=17$)
			& 8.294 & 8.529 & 7.824 & 7.941 & 6.059
			& 3.529 & 3.324 & 4.588 & \underline{2.500} & \textbf{2.412} \\
			\midrule
			\multirow{6}{*}{Type $T$}
			& Biomedical ($n=10$)
			& 9.300 & 8.900 & 7.800 & 6.800 & 4.800
			& 4.100 & \textbf{3.000} & 4.300 & \textbf{3.000} & \textbf{3.000} \\
			& Industrial ($n=21$)
			& 7.857 & 7.690 & 6.690 & 8.047 & 5.476
			& 4.476 & 3.976 & 4.571 & \underline{3.357} & \textbf{2.857} \\
			& Motion ($n=17$)
			& 8.000 & 7.941 & 6.529 & 8.206 & 5.971
			& 4.029 & 3.441 & 5.647 & \underline{2.971} & \textbf{2.265} \\
			& ImageOutline ($n=20$)
			& 7.850 & 7.900 & 7.150 & 8.400 & 5.300
			& 3.675 & 4.450 & 4.800 & \underline{2.875} & \textbf{2.600} \\
			& Spectral ($n=11$)
			& 8.545 & 8.818 & 7.773 & 7.773 & 6.091
			& 2.955 & 4.455 & 4.136 & \underline{2.409} & \textbf{2.045} \\
			& Simulated ($n=7$)
			& 7.857 & 9.286 & 7.000 & 8.857 & 6.143
			& 2.786 & 5.000 & 3.786 & \textbf{2.071} & \underline{2.214} \\
			\bottomrule
	\end{tabular}}
\end{table*}

\subsubsection{Contribution of the Evolutionary Program Construction}
The first perspective demonstrates the contribution of the evolutionary program construction process by comparing EvoTSC against variants that bypass evolution entirely and rely solely on predefined feature extraction operators. Specifically, four variants are constructed by directly applying a single extraction operator (ShapeInc, ShapeDec, ShapePeak, or StatisDist) to the raw time series. In addition, a fifth variant, denoted AllFea, applies all four extraction operators and concatenates the resulting feature vectors into a single representation, providing an upper-bound baseline for non-evolutionary feature extraction. As shown in Table~\ref{tab:ablation}, the four single-operator variants consistently occupy the lowest-ranked positions across all fourteen dataset groups. This  demonstrates that applying a single predefined extraction operator to the raw time series, without the evolutionary program construction, yields features of limited discriminative power. Furthermore, while AllFea consistently outperforms the individual operators by leveraging the complementarity among different extraction operators, it exhibit noticeable degradation relative to the full EvoTSC in every dataset group. This gap confirms that the performance gains of EvoTSC are not merely attributable to the availability of diverse extraction operators, but rather stem from the ability of the evolutionary search to discover task-specific program compositions tailored to the characteristics of target dataset.

\subsubsection{Contribution of the Multi-layer Program Structure}
The second perspective investigates the contribution of the functional layers within the proposed multi-layer program structure through three degraded variants. The first variant, wo\_Dom, removes the domain transform layer to examine whether allowing the evolutionary search to exploit frequency-domain and difference-domain representations contributes to the performance. The second variant, wo\_Patch, removes the content-adaptive patching layer to assess whether segmenting the input into overlapping patches, rather than treating the full segment as a single extraction unit, enhances feature learning. The third variant, wo\_Con, removes the feature concatenation layer to examine whether allowing the evolution to simultaneously utilize features from multiple sources contributes to the performance. It can be seen from Table \ref{tab:ablation} that all three layer-removal variants exhibit degradation relative to the full EvoTSC across all the dataset groups, confirming that the functional layers contribute positively to the overall feature learning process.

\subsubsection{Effectiveness of the Pareto Tournament Selection}
The third perspective examines the effectiveness of the tailored Pareto tournament selection strategy. In this variant, denoted as wo\_Pareto, the tailored Pareto tournament selection is replaced with standard tournament selection, where the single averaged cross-validation accuracy serves as the selection criterion. As reported in Table~\ref{tab:ablation}, this modification leads to performance degradation relative to the full \textsc{EvoTSC} in eleven out of fourteen dataset groups, with only two groups showing a tiny advantage for wo\_Pareto. This confirms that the proposed selection strategy effectively enhances the generalizability of learned features by filtering out candidate models that overfit to specific folds.

In summary, the ablation results demonstrate that each component of EvoTSC contributes meaningfully to the overall performance, collectively enabling the proposed approach to evolve effective and generalizable feature learning models for TSC.

\subsection{Analysis of the Evolved Individuals}
\label{s62}
\subsubsection{Structural Composition Analysis of Evolved Individuals}
The first experiment examines the structural composition of the evolved individuals across all datasets, aiming to answer a central question: what structural preferences does evolution discover across different categories of TSC problems, and what implicit domain knowledge do these preferences reveal?

We collect the evolved individual from each of 30 independent runs for each of the 86 UCR datasets, yielding 2{,}580 program trees in total. Following the three grouping schemes introduced earlier, the operation usage within each dataset group is counted and the proportion of each operation is computed. For the feature concatenation layer operations, proportions are calculated relative to the total number of concatenation nodes in the corresponding group. For all other operations, proportions are calculated relative to the number of feature learning branches in that group. The following observations can be drawn from the heatmap in Fig.~\ref{heatmap}.
\begin{figure*}[t]
	\centering
	\includegraphics[width=1\textwidth]{figs/heatmap_operator_proportions.png}
	\vspace{-20pt}
	\caption{Heatmap of operation proportions across different dataset groups. Datasets are grouped by number of classes, time-series length, and data type. \textbf{Segment Dectection (Seg.)}: \textit{SegDect} indicates the proportion of branches that use segment detection. \textbf{Domain Transform}: \textit{Raw} denotes the proportion of branches that operate directly in the original domain without applying any transformation; \textit{Freq} and \textit{Diff} denote frequency transform and differencing, respectively. \textbf{Content-Adaptive Patching}: $D=i$ indicates that the length of patches is $\frac{\ell_{\text{in}}}{i}$; \textit{No\,Patch} indicates that no patching operation is applied in the branch. \textbf{Feature Extraction}: values represent the proportions of different extraction operator, where \textit{Shape} aggregates all shape-related extraction operations.}
	\label{heatmap}
\end{figure*}

For segment detection usage across application types, the \emph{Biomedical} group exhibits the highest proportion ($65.8\%$), far exceeding all other groups. This is consistent with clinical practice, where localizing specific waveform components, such as the QRS complex in ECG signals or characteristic deflections in EOG recordings, is essential for diagnosis. Across different series lengths, the segment detection rate rises from $36.4\%$ for the \emph{151\,$\leq$\,L\,$\leq$\,500} group to $45.1\%$ for the \emph{L\,$>$\,1000} group, consistent with the intuition that longer sequences are more likely to contain task-irrelevant or noisy regions, making explicit subsequence localization increasingly beneficial.

For domain transform usage across application types, the \emph{Industrial} group shows the highest proportion of difference domain usage ($38.1\%$), aligning with the nature of industrial monitoring signals, where abrupt state transitions and relative temporal variations often carry discriminative information. Conversely, the \emph{Spectral} group exhibits the highest raw domain usage ($77.0\%$). While this may appear counter-intuitive, the raw signals in these UCR datasets are already spectral curves, so the discriminative information inherently resides in the original domain. Applying a further frequency transform would amount to a redundant second-order transformation, and evolution therefore overwhelmingly favors operating directly in the original domain.

For the proportions of concatenation operators across different numbers of classes, the proportion of $\operatorname{\mathbf{FeaConH}}$ increases as the number of classes grows, from $33.4\%$ in the \emph{C\,=\,2} group to $49.0\%$ in the \emph{C\,$>$\,10} group. This is consistent with the intuition that more complex classification tasks with a larger number of classes require richer feature representations to construct sufficiently discriminative boundaries.

Overall, these results indicate that evolution is able to discover some structural preferences across different categories of TSC problems, and that the resulting preferences reveal meaningful implicit domain knowledge about how discriminative representations should be learned.
\begin{figure}[t]
	\centering
	\includegraphics[width=0.45\textwidth]{figs/case_study5.png}
	\vspace{-5pt}
	\caption{Case study on the ECG5000 dataset. (a)~Visualization of the training instances, where different colors denote different classess. (b)~Two evolved individuals, where each $\operatorname{\mathbf{SegDect}}$ node has a left terminal indicating the segment length and a right terminal indicating the starting position.}
	\label{casestudy}
\end{figure}

\subsubsection{An Example of the Evolved Individuals}
This section presents a case study to investigate whether the decision-making process of evolved individuals can be logically inspected and whether they can selectively focus on discriminative segments within a time series. ECG5000 is used as the example dataset, as ECG signals possess well-understood morphological components, which provide a clinical reference for verifying whether the detected segments are physiologically meaningful.

For each class, the per-time-step mean and standard deviation across all training instances are computed and visualized as solid curves with shaded bands in Fig.~\ref{casestudy}(a). This representation is adopted because plotting all raw instances would be visually cluttered, while displaying only a subset could give a biased impression. Furthermore, two  evolved program trees from this dataset are illustrated in Fig.~\ref{casestudy}(b), and the three segments they detect ([A],[B] and [C]) are highlighted on the corresponding regions in Fig.~\ref{casestudy}(a).

It can be seen that evolved individuals provide a clear decision process. For instance, analyzing the rightmost feature-learning branch of the left individual in Figure~\ref{casestudy}(b), the original time series is first truncated to a segment starting at index 103 with a length of 21 (i.e., the interval $[103, 123]$). This segment is then transformed into the frequency domain via the $\operatorname{\mathbf{DomFreq}}$ operator, followed by a patching operation ($\operatorname{\mathbf{AdaPatch}}$) with a patch size of $\lfloor \ell_{\text{in}}/16 \rfloor$. Finally, the $\operatorname{\mathbf{ShapePeak}}$ operator is applied to extract features from the frequency representation. Such explicit, step-by-step reasoning empowers domain practitioners to logically inspect the model's decision-making process.
	
Moreover, the segments highlighted by the evolved individuals exhibit clear inter-class separability. As illustrated in Fig.~\ref{casestudy}(a), Segment~[C] (positions $[1,36]$) covers the initial part of the heartbeat, where pronounced inter-class differences can be observed. This region contains a sharp deflection, suggesting that it corresponds to the clinically informative QRS complex in ECG interpretation. Segments~[A] (positions $[111,140]$) and~[B] (positions $[103,123]$) jointly span the terminal portion of the heartbeat, a region likely corresponding to the T-wave and the subsequent recovery phase. This region also exhibits greater inter-class separation than the middle portion of the series. These observations suggest that the evolutionary search can naturally identify and focus on physiologically meaningful regions.

Overall, this case study demonstrates that EvoTSC can evolve potentially interpretable models whose internal logic can be verified against domain expertise, a property particularly valuable in safety-critical applications.

\subsection{Analysis on Computational Cost of the Evolved Models}
\label{s63}
This experiment evaluates the resource efficiency of EvoTSC by analysing two hardware-independent metrics: floating-point operations (FLOPs), which reflect inference latency, and peak memory usage (in bytes), which reflects memory consumption during inference \cite{lin2020mcunet}. This analysis is conducted on the ECG5000 dataset, chosen because ECG monitoring on wearable or implantable devices is an important resource-constrained real-world application \cite{ECGTCN,pramukantoro2025real}.

Fig.~\ref{fig:resource} plots FLOPs against peak memory usage on a log-log scale \cite{11030860} for EvoTSC and five comparison methods. To make these values more intuitive for real-world applications, we map them against the hardware constraints of two widely used commercial microcontrollers: the STM32F446RE \footnote{https://www.st.com/en/microcontrollers-microprocessors/stm32f446re.html} (operating at up to 180 MHz with 128 KB SRAM) and the STM32L552ZE \footnote{https://www.st.com/en/microcontrollers-microprocessors/stm32l552ze.html} (operating at up to 110 MHz with 256 KB SRAM) \cite{king2025micronas}. The vertical dashed lines indicate the SRAM limits of each microcontroller, while the horizontal dashed lines represent the estimated upper bounds on FLOPs that can be completed within a 100\,ms real-time response budget at the respective maximum clock frequencies.
\begin{figure}[ht]
	\hspace*{-0.3cm} 
	\includegraphics[width=0.95\linewidth]{figs/deployment.png}
	\vspace{-5pt} 
	\caption{Resource consumption comparison between EvoTSC and baseline methods on the ECG5000 dataset.}
	\label{fig:resource}
\end{figure}

As shown in Fig.~\ref{fig:resource}, EvoTSC occupies the lower-left region of the plot, requiring approximately $10^{4}$ FLOPs and only a few kilobytes of peak memory. It falls comfortably within the feasible deployment zone of even the more constrained STM32F446RE microcontroller, leaving substantial headroom in both the computational and memory dimensions. In contrast, the NN-based methods demand over $10^{8}$ FLOPs and exceed $10^{5}$ bytes of peak memory, completely surpassing the physical SRAM capacity and the 100\,ms latency budget of both evaluated microcontrollers. The foundation-model methods exhibit even more prohibitive resource consumption, with TiViT reaching approximately $10^{11}$ FLOPs and $10^{7}$ bytes of peak memory. This substantial reduction in resource consumption stems from the fact that, rather than relying on large parameter matrices and dense tensor multiplications, the feature learning model evolved by EvoTSC is prensented in concise, symbolic programs. These results demonstrate that EvoTSC offers a highly practical pathway in resource-constrained environments where deep neural network approaches remain impractical.

\section{Conclusions and Future Work}
\label{s7}
This paper proposed EvoTSC, a GP-based approach that automatically evolves lightweight and effective feature learning models for TSC. The key insight behind EvoTSC is that by embedding diverse forms of prior expert knowledge into a carefully designed multi-layer program structure, the evolutionary search can be guided to discover effective compositions of TSC-specific operations tailored to target dataset. Additionally, a tailored Pareto tournament selection strategy is introduced to enhance the generalizability of the learned features by favoring models that generalize well across varying data subsets during the evolutionary search.

Experimental results yielded several important findings. First, EvoTSC achieves the best overall rank among eleven benchmark methods, demonstrating the value of GP as a promising alternative for TSC. Second, ablation studies confirm that each proposed component contributes meaningfully to the overall performance. Finally, further analyses show that EvoTSC evolves models whose internal logic can be verified against domain expertise and whose resource consumption is orders of magnitude lower than that of NN-based methods.

Despite the promising results, several directions remain open for future investigation. First, the current work focuses exclusively on univariate time series. Extending EvoTSC to handle multivariate time series, where cross-variate dependencies carry additional information, is a natural and important direction. This extension may require redesigning the program structure to incorporate cross-variate operators that can capture correlations among multiple variates. Furthermore, the current approach evolves feature learning models independently for each dataset. Investigating how to transfer or reuse building blocks, such as effective subtree structures, across related datasets could potentially accelerate the evolutionary search and improve performance on label-limited tasks.


\bibliographystyle{IEEEtran}
\bibliography{refs}



\end{document}


