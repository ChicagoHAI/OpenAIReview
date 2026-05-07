\PassOptionsToPackage{numbers,square}{natbib}

\documentclass[reprint,amsfonts, amssymb, amsmath,  showkeys,pra,nofootinbib, twocolum,longbibliography,aps, superscriptaddress]{revtex4-2}

\usepackage[dvipsnames,table]{xcolor}
\usepackage{graphicx}
\usepackage{float}
\usepackage[caption = false]{subfig}
%\usepackage{svg}
\usepackage{soul}
\usepackage{ulem}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage[numbers]{natbib}
\usepackage{comment}
\usepackage{array}
\usepackage{braket}

\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}

\newcommand{\alba}[1]{\textcolor{Red}{\textbf{Alba: } #1}}

\newcommand{\bsc}{Barcelona Supercomputing Center (BSC)
}
\newcommand{\upf}{BCN Medtech, Universitat Pompeu Fabra, Barcelona, Spain}
\newcommand{\uba}{Departament de Física Quàntica i Astrofísica, Facultat de Física,
Universitat de Barcelona, E-08028 Barcelona, Spain}
\newcommand{\ubb}{Institut de Ciències del Cosmos, Universitat de Barcelona,
ICCUB, Martí i Franquès 1, E-08028 Barcelona, Spain.}
\newcommand{\icrea}{ICREA, Barcelona, Spain.}

\begin{document}


\title{Towards interpretable AI with quantum annealing feature selection}

\author{Francesco Aldo Venturelli}
\affiliation{\upf}
\affiliation{\bsc}
\author{Emanuele Costa}
\affiliation{\bsc}
\author{Sikha O K}
\affiliation{\upf}
\author{Bruno Juliá-Díaz}
\affiliation{\uba}
\affiliation{\ubb}
\author{Miguel A. González Ballester}
\affiliation{\upf}
\affiliation{\bsc}
\affiliation{\icrea}
\author{Alba Cervera-Lierta}
\affiliation{\bsc}


\begin{abstract}

Deep learning models are used in critical applications, in which mistakes can have serious consequences. Therefore, it is crucial to understand how and why models generate predictions. This understanding provides useful information to check whether the model is learning the right patterns, detect biases in the data, improve model design, and build systems that can be trusted. This work proposes a new method for interpreting Convolutional Neural Networks in image classification tasks. The approach works by selecting the most important feature maps that contribute to each prediction. To solve this combinatorial problem, we encode it into a quantum constrained optimization problem and propose to solve it using quantum annealing. 
We evaluate our method against the state-of-the-art explainable AI techniques, specifically GradCAM and GradCAM++,
and observe an improved class disentanglement, i.e. the model's decision boundaries become more distinct and its reasoning more transparent. This demonstrates that our approach enhances the quality of explanations, making it easier to understand which features the model relies on for specific predictions. In addition, we study the computational behavior of the quantum annealing algorithm. Specifically, we analyze the minimum energy gap of the system during computation and the probability that the algorithm finds the correct solution. These analyses provide theoretical insight into why the method works effectively in practice.

\end{abstract}

\maketitle

\section{Introduction}\label{sec:intro}

Deep learning (DL) has emerged as the standard approach to solving computer vision problems. One of the most relevant contributions of DL is the introduction of the Convolutional Neural Network (CNN)~\cite{lecun1998convolutional}. CNN sequentially applies convolution operations that learn local spatial correlations, ensuring that the data-dimension is consecutively increased across multiple layers while higher-level features are extracted.

Different CNN architectures have been proposed and explored so far. The first breakthrough in CNNs began with AlexNet. Subsequent architectures such as VGGNet and ResNet demonstrated that shallower structures and the removal of residual connections could significantly improve representation learning and training stability, becoming widely used backbone models for visual recognition systems.

Despite their success, DL models often behave as ``black boxes''. To address this limitation, the field of explainable AI (XAI) has emerged. XAI methods are broadly categorized into \textit{ante-hoc}, which analyze trained models after the fact, and \textit{post-hoc} approaches, which incorporate interpretability constraints during model design. 

In the field of interpretability, CNNs are relatively easy to work with. Examples are Grad-CAM and Grad-CAM++, which compute the gradients of a target class score with respect to the input pixels, producing coarse localization maps that highlight image regions that most influence the prediction. 

These methods, however, operate at an aggregate level. They combine contributions from all feature maps (FMs) into a single saliency visualization, which successfully disentangles the role of individual FMs within the network and clarifies which specific learned representation is responsible for a given prediction.

A promising direction lies in feature selection (FS). However, it is known that FS is computationally trivial, since searching a subset of features that satisfies a certain condition scales linearly with the number of features in the search space. For this reason, simple exhaustive search is the standard approach.

In this work, we explore the novel use of quantum computing for FS. By mapping the FS task into a Quadratic Unconstrained Binary Optimization (QUBO) formulation, each binary variable represents a continuous weight. Within this framework, quantum computers enable the exploration of the solution space by considering candidate solutions sequentially rather than in parallel.

Reformulating FS schemes as a QUBO problem is not a novel attempt. Although current Noisy Intermediate-Scale Quantum (NISQ) devices already guarantee a definitive quantum advantage over classical solvers, they are rarely used for high-dimensional FS problems due to their lack of noise.

In this work, we propose a quantum annealing (QA)-based FS approach. We enforce the QA to sample the bit-string that minimizes the linear importance of a single FM while maximizing the geometrical similarity among distinct FMs through the cosine similarity term, to ensure redundant representations are preserved.

Reducing the number of FMs by FS schemes provides a natural strategy to increase scalability and dimensionality challenges in DL models. Additionally, it improves model interpretation by isolating FMs that have no contribution to a given prediction, ensuring the most redundant patterns are learned. 

The article is organized as follows: in sec. \ref{sec:results} we give a detailed description of the FS algorithm, defining the mathematical formulations and the QA simulation procedure. Subsequently, we present the main results, i.e. the explanation maps sampled by QA and the class-class correlation maps that quantify the disentanglement among distinct image classes. Then, we analyze the model's success by defining physics-derived metrics, such as the maximum energy gap between the first excited state and the ground state of the QUBO Hamiltonian and we explain the meaning behind these results. 


\section{Results}\label{sec:results}

\subsection{Quantum annealing feature map selection algorithm}

\begin{figure*}[t!]
    \centering
    \includegraphics[width=1\textwidth]{main_figure.pdf}
        \caption{
        Representation of the FS algorithm reformulated as a QUBO problem. $1-2)$ A single image is fed into a CNN that has been previously trained. From the last convolutional layer we extract the FMs $f^{(a)}_{ij}(x)$, with $(a) \in N_f$.
        3) A one-hot encoding is applied to the FMs that contribute positively to the gradient.
        4) We construct the global problem Hamiltonian, prepare the initial quantum state in superposition of all possible $N_f$ combinations and we use QA to evolve the state towards the minimum of the QUBO Hamiltonian.
        5) Finally, we sample the resulting bitstring, which corresponds to the explanation map containing the FMs that satisfy the constraints imposed by the problem Hamiltonian: maximizing the positive contribution of each FM while minimizing their geometrical similarity.
        This pipeline is repeated for $M$ images from the test set.}
    \label{fig:MainFigure}
\end{figure*}

As mentioned in the introduction, we propose a XAI method that identifies the relevant FMs needed to classify a given image. To do so, we encode the optimization problem of finding this set into a QUBO problem and solve it with QA.
The overview of our algorithm, as shown in Fig.~\ref{fig:MainFigure}, is the following: we take the FMs produced from the last convolutional block and select those whose gradient positively contributes to the model's output (importance measure). We then generate an Ising-type Hamiltonian using the absolute value of the cosine similarity between the FMs and the importance of each FM. The QA evolves the corresponding Hamiltonian to find the ground state containing the superposition of the FMs relevant for the image. By repeating this process for the whole image dataset, we extract a class correlation map that allows us to interpret which classes share common FMs. In other words, we disentangle the FMs from the CNN to obtain only those relevant to identify the image class.

Formally, a CNN is a parametric function composed of convolutional operators that map an image $\mathbf{x}\in \mathbb{R}^{H\times W\times C}$, where $H$ and $W$ are the height and width of the image (e.g. the number of pixels that it contains), and $C$ is the channel (e.g. $C=3$ for RGB), to hierarchical FMs, followed by a dense classifier operating on the learned representations. Each convolutional layer takes as input the FMs produced by the previous layer and applies learnable filters to extract higher-level features; the spatial dimensionality is reduced through sequences of striding or pooling operations. In a ResNet architecture, each convolutional layer produces a fixed number of FMs determined by the number of trainable 
filters. While the number and dimensions of these FMs are the same for all inputs, the activation values within them differ for each image because they depend on the specific patterns present in the input. Therefore, after training the CNN on a given dataset, each input image produces a set of FMs whose activation values depend on the patterns present in that image. While images belonging to the same class often generate similar activation patterns, the learned filters themselves are not explicitly labeled, and it is generally not straightforward to interpret what specific semantic feature each filter represents.

Given the set of FMs from the last convolutional layer, $\{\mathbf{f}\}\in \mathbb{R}^{H_{f}\times W_{f}\times N_{f}}$, where $H_{f}$ and $W_{f}$ are the height and width of the last layer (typically, way smaller than the image $H$ and $W$) and $N_{f}$ is the number of the learned representations (that depends on the CNN architecture, but typically much larger than $C$), and the final output of the dense classifier, $z=\text{CNN}(\mathbf{x})$, where $\text{CNN}$ represents the full CNN processing layers, we compute the following quantity
\begin{equation}
    \alpha_a=\frac{1}{H_{f} W_{f}}\sum_{ij}^{H_{f}, W_{f}} \frac{\partial z}{\partial f^{(a)}_{ij}},
    \label{eq:alpha}
\end{equation}
for each FM $a$, which is the global average pooling of the gradient. This quantity is equivalent to obtaining a scalar measure of the importance for each FM. In the GradCAM approach, $\alpha_a$ is just the weight of the corresponding FM. Depending on the sign of $\alpha_a$, we can distinguish class-confirming FMs (positive sign), which contribute to characterizing the class, and class-opposing ones (negative sign) that pivot on characterizations that lower the confidence of the classification. In our approach, we propose a \textit{filtered} GradCAM, i.e. $f$GradCAM, by selecting the learned representations that satisfy
\begin{equation}
    \{\tilde{\mathbf{f}}\} \equiv \{\mathbf{f}^{(a)}|\alpha_{a}>0\}.
\end{equation}
Notice that each $\tilde{\mathbf{f}}\in\mathbb{R}^{H_{f}\times W_{f}}$ and there will be $d\leq N_{f}$ filtered FM. 

Next, we compute the cosine similarity between the pairs of filtered FM, 
\begin{equation}
J_{pq}=| \langle \tilde{\mathbf{f}}^{(p)}; \tilde{\mathbf{f}}^{(q)}\rangle |=\frac{|\sum_{ij} \tilde{f}_{ij}^{(p)} \tilde{f}_{ij}^{(q)}|}{||\tilde{\mathbf{f}}^{(p)}||\  ||\tilde{\mathbf{f}}^{(q)}||}.
\label{eq:cos_sim}
\end{equation}
This quantity is large when there is overlap and, therefore, redundancy between distinct FMs, while it is small when the FMs are more geometrically independent. The idea behind the cosine similarity is to assume that FMs that encode similar information, which is redundant for the model, are parallel vectors in the feature latent space. Thus, we look for the subset of vectors that are maximally orthogonal to each other.

Our goal is to select the subset of positive representations maximizing the importance of the filtered FM, $\tilde{\alpha}>0$ (gradient) and minimizing the redundancy $J_{pq}$ (cosine similarity) between the filtered FMs. To do so, we propose a one-hot encoding for the filtered FM, representing each of them as a unary vector $\hat{n}_{p}\equiv\frac{1-\sigma_{z}^{(p)}}{2}$, where $\sigma_{z}=\mathrm{diag}(1,-1)$ is the Pauli-Z operation acting on qubit $p$. Therefore, we will need $d$ qubits to represent the space of filtered FMs. Next, we construct a QUBO Hamiltonian of the following form:
\begin{equation}
    \hat{H}_{\text{QUBO}} = (1-\beta) \frac{1}{2}\sum_{pq} J_{pq} \hat{n}_p\hat{n}_q + 
    \beta\sum_p h_p \hat{n}_p.
    \label{eq:QUBO_hamiltonian}
\end{equation}
The transverse field encodes the importance of the filtered FMs
\begin{equation}
 h_p=\frac{\tilde{\alpha}_p }{\max \tilde{\alpha}_p},
\end{equation}
such that its values range in $h_p \in [0,1]$. Finally, $\beta$ is a hyperparameter that defines the interplay between the two terms.
For $\beta=1$ all the positive FMs are selected. Conversely, smaller $\beta$ values weaken this bias and encourage QA to explore a broader subset of FMs, thereby incorporating contributions from less dominant gradient components. In the limit $\beta=0$, only cosine similarity is considered, i.e. there are no constraints on the number of selected FMs and the solution will be the trivial null set.
In our analysis, we set $\beta=0.7$ as we numerically observed the results were better if we gave slightly more weight to the importance.

The QA protocol starts with initializing the qubits in the ground state of a driver Hamiltonian  $\hat{H}_{D}=-\sum_{p}^{d}\hat{\sigma}_{x}^{(p)}$, i.e. in the full superposition state of all the bit-strings that encode all possible subsets of FMs $\ket{\psi}_{\mathrm{init}}=\bigotimes_{p=1}^{d} \ket{+}_p$, i.e. $\ket{\psi}_{\text{init}} = \frac{1}{2^{d/2}}\sum_{z\in \{0,1\}^{d}}\ket{z}$.
Here,\\ $\sigma_x = \begin{pmatrix}
    0 & 1 \\
    1 & 0
\end{pmatrix}$ represents the Pauli$-$X operator acting on qubit $p$.
The dynamics is governed by a time-dependent Hamiltonian 
\begin{equation}
    \hat{H}(s)=A(s) \hat{H}_\text{D} + B(s) \hat{H}_{\mathrm{QUBO}},
    \label{eq:HP}
\end{equation}
where $s$ is the dimensionless time parameterized as $s\equiv\frac{t}{\tau}$, where $\tau$ is the total evolution time, $t$ is the time and $A(s)$ and $B(s)$ satisfy the conditions $B(0)=0$, $A(1)=0$. In our case, we chose a linear interpolation between $A$ and $B$, i.e. $A(s)=1-s$ and $B(s)=s$.

Notice that the combinatorial optimization problem grows exponentially with the number of filtered FM $d$ (the Hilbert space has dimensions $2^{d}$), while by solving it with a QA protocol, the final solution after the evolution is sampled using a polynomial number of shots, typically $n_{\text{shots}}=O(d^2)$.

\subsection{Benchmark}

\begin{figure*}[t!]
    \centering
    \includegraphics[width=9cm]{orthogonal_matrix_tau50_qa.pdf}%
    \includegraphics[width=9cm]{orthogonal_matrix_sa.pdf}
    \caption{(Top) Class–class correlation map for the FS algorithm for a ResNet-18 constrained to $N_{f}=16$ FMs in the final layer and trained for 20 epochs.
    Warmer colors indicate stronger overlap between FMs.
    The matrix is obtained by computing the scalar product between the distributions of the activated FMs per image class, i.e. the Bhattacharya coefficient.
    In the QA simulation, we set $\tau=50$ and $n_{\text{shots}}=d^2$, where $d$ is the number of FMs that contribute positively to the output's gradient. A full diagonal matrix indicates complete orthogonality among classes. Values below $0.10$ are rounded to $0$.
    (Bottom) Class–class correlation map for FS algorithm using SA for the full ResNet-18 model trained for 100 epochs. For $N_{f}=512$, the SA is able to find a good disentanglement between hidden learned representations.}
    \label{fig:CC-corr}
\end{figure*}

\renewcommand{\arraystretch}{1.2} 


\begin{table*}[t!]
\centering
%\begin{tabular}{ |p{1.8cm}||C{2cm}|C{2.5cm}|C{3cm}||C{2cm}|C{2.5cm}|C{3cm}| }
\begin{tabular}{|c|c|c|c||c|c|c|}
 \hline
 \multicolumn{7}{|c|}{\textbf{Quantitative analysis - Average Drop $\%$}} \\
 \hline

 \multirow{2}{*}{\textbf{Class}} 
 & \multicolumn{3}{c||}{$\mathbf{N_f = 16}$}
 & \multicolumn{3}{c|}{$\mathbf{N_f = 512}$} \\
 
 \cline{2-7}

 & \textbf{GradCAM} & \textbf{GradCAM++} & \textbf{QA-$f$GradCAM}
 & \textbf{GradCAM} & \textbf{GradCAM++} & \textbf{SA-$f$GradCAM} \\
 \hline

 0 Airplane  &33.1 &17.1 & 13.8 &1.20 &2.29 & 12.9\\
 \hline
 1 Bird &14.4 &13.4 & 7.06 &4.76 &4.02 & 23.3\\
 \hline
 2 Car &3.87 &0.44 &0.67 &0.97 &1.38 & 8.09\\
 \hline
 3 Cat &11.6 &17.0 & 4.99 &4.29 &1.29 & 14.0\\
 \hline
 4 Deer &24.8 &4.21 &14.5 &5.11&5.27 & 6.47\\
 \hline
 5 Dog &63.3 &56.65 &56.9 &12.1 &17.0 & 30.1\\
 \hline
 6 Horse &7.90 &8.75 & 3.43 &7.31 &12.4 & 32.6 \\
 \hline
 7 Monkey &16.2 &6.36 & 4.18 &13.0 &18.9 & 34.0 \\
 \hline
 8 Ship &0.72 &0.25 &0.70 &0.97 &1.59 & 14.9\\
 \hline
 9 Truck &0.22 &1.11 & 0.14 &2.88 &3.01 & 7.37 \\
 \hline

 $\mathbf{\overline{x} \ \pm \ \sigma_{\overline{x}}}$ 
 &17.6 $\pm$ 5.74 
 &13.2 $\pm$ 4.97 
 &$\mathbf{10.6\pm5.11}$ 
 &$\mathbf{5.26\pm1.31}$ 
 &6.73 $\pm$ 2.04 
 &$18.4\pm3.22$\\
 \hline

\end{tabular}
\caption{Comparison between GradCAM, GradCAM++ and our QA-$f$GradCAM protocol in terms of the Average Drop $\%$ per image class. The QA simulation takes $\tau=50$ and $n_{\text{shots}} = {d}^2$, where $d$ is the number of filtered FMs for each image. Out method performs better than GradCAM and in most classes also better than GradCAM++.
}
\label{tab:performance}
\end{table*}

\begin{figure*}[t!]
    \centering
    \includegraphics[width=15cm]{gradcams_results.pdf}
    \caption{Qualitative comparison example of GradCAM and GradCAM++ with our QA-$f$GradCAM protocol for $N_{f}=16$ and $\tau=50$. The selected representations capture relevant regions and seem to identify parts of the images that are misinterpreted by the state-of-the-art methods.}
    \label{fig:Airplanes}
\end{figure*}

To validate the proposed method, we take the STL-10 \cite{coates2011analysis} dataset that contains 5000 images in total that belong to 10 distinct classes (for more details, check the \ref{sec:dataset} section). As a CNN architecture, we use a pretrained ResNet-18. An important point in our benchmarks is that we need to constrain the maximum number of FMs in the last convolutional layer, $N_f$, to simulate the QA protocol. If we had access QA hardware, this step would not be necessary, since state-of-the-art QAs contain more than 1000 qubits. We study the scalability of our simulations by increasing $N_f$ from 16 up to 32 FMs. Moreover, we also run a simulated annealing (SA) protocol with all $N_f=512$ FMs to obtain an estimation of the protocol's success, although this final simulation will not give the relevant physical properties necessary to understand the physical limitations of this protocol. 


We start by obtaining the confusion matrix by computing the Bhattacharyya coefficient~\cite{patra2015new}, which estimates how likely two classes share the same FMs.
A fully diagonal correlation matrix indicates well-separated (i.e., disentangled) FMs that capture information specific to a single image class. In contrast, non-zero off-diagonal elements reveal shared representations among different image classes and constitute the primary source of false-positive and true-negative errors.

Figure~\ref{fig:CC-corr} shows the class-class correlation map for a CNN restricted to $N_{f}=16$ filtered FMs (top) and for the full ResNet-18 with all the $N_{f}=512$ FMs. In the first case, we can analyze the physical aspects of the protocol, as will be shown in later sections, while for the full ResNet case we use SA. In both cases, the matrix shows an overall good disentanglement across different image classes.
Focusing on the $N_{f}=16$ case, we obtain only $15$ non-zero ($\geq 0.1$) overlap out of the $44$ possible image class combinations, and all of these lead to a Bhattacharya coefficient below $0.5$.
We leave a formal explanation of the results in the section  \ref{sec:discussion}.
For the full FMs simulation, we mostly disentangle completely all the classes.

We then test our proposed FS against well-known classical methods that have achieved promising results and constitute the state-of-the-art in the context of interpretability. Specifically, we compare the explanation maps obtained by our protocol with $N_{f}=16$ against the spatial projections originated by GradCAM and GradCAM++ for the entire set of image classes. As a qualitative example, Figure \ref{fig:Airplanes} shows different explanation maps that highlight the images for the specific class of airplane images. 
The explanation map derived by the QA-$f$GradCAM is a bit string containing the FMs that satisfy the constraints of the QUBO problem (positive gradient contribution and maximal orthogonality between FMs), as explained in the previous section. In this way,  we expect to obtain GradCAM and GradCAM++ which contain less spurious representations compared to the filtered one.

To obtain a quantitative analysis, we estimate the $\text{Average Drop}\  \%$ ~\cite{chattopadhay2018gradcampp} (see Sec.\ref{sec:average_drop} for details) which essentially replaces all the pixels of the image that are excluded by the explanation map to 0 (i.e. set them to black), and then inputs this new image to the model to calculate the prediction score (accuracy). Therefore, the lesser $\text{Average Drop}\  \%$, the better, which implies that the explanation map obtained was already optimal and that change in the pixels does not significantly modify the accuracy of the model.
Table \ref{tab:performance} shows the Average Drop $\%$ per class for the different methods. QA-$f$GradCAM achieves on average better results compared to GradCAM and GradCAM++. From the 10 classes, only in 4 of them GradCAM++ achieves better results than QA-$f$GradCAM.
On the contrary, when the initial number of FMs is increased to 512, our method shows worse behavior compared to the classical counterparts. Despite the apparent challenge, we give in the next section \ref{sec:discussion} a possible explanation on why this potentially occurs for the current set-up of parameters we use.

\subsection{Model's efficiency and success}

We now proceed to analyze in detail the physical properties of the QA protocol to address its efficiency and success. In QA, a relevant quantity to determine the model's complexity is the energy gap $\Delta_{\min}\equiv E_{1}-E_{0}$ between the ground state and 1st excited state energies of the time-dependent Hamiltonian $\hat{H}(s)$ from Eq.~\eqref{eq:HP}. If $\Delta_{\min}$ tends to zero, the annealing time parameterized by $s$ must be longer to ensure that the system remains in its ground state (for more details, see Sec.~\ref{sec:complexity}). 

\begin{figure}[t!]
    \centering
    \includegraphics[width=0.9\linewidth]{delta_distribution_tau50.pdf}
    \caption{Energy gap $\Delta_{\min}$ distribution for $N_f=16$, for $\tau=50$ and $\Delta s=0.01$ across all 200 samples of the test set. In purple, the cumulative distribution tells us about how likely we find values of the minimum gap.
    }
\label{fig:delta_cummulative}
\end{figure}

We start with an aggregated analysis of the gap for all the dataset. For each image, we diagonalize $\hat{H}(s)$ to obtain its spectrum and compute the $\Delta_{\min}$ for time steps of $\Delta s = 0.01$ and $\tau=10$. In Fig.~\ref{fig:delta_cummulative} we plot the histogram and the cumulative curve.
We observe that the overall trend is placed towards large energy gap values, near $10^{-1}$ unit of energy, while the
probability of having values below $10^{-3}$ is very close to $0$. This indicates that the QA evolution is sufficient and robust to converge to the ground state of the target problem Hamiltonian $\hat{H}_\text{QUBO}$ for most of the instances of the QUBO problem.

Next, we investigate the probability of success, i.e. of finding the true ground sate, of the QA protocol for each image. We compute the fidelity $F$ (i.e. a measure of distance) between the quantum state obtained after the QA evolution and the exact ground state of $\hat{H}(s)$. For a random final state, $\bar{F}\simeq \frac{1}{2^{d}}$, i.e. a uniform distribution. In general, any scaling of $F$ of the type $F \propto d^{-\gamma}$, with $\gamma >0$ is considered a good result, since it restricts the research method to a subspace polynomial with the degrees of freedom of the system.

One would expect that for low values of $\tau$, the evolution will not be adiabatic and the system will end up in an excited state instead of the ground state. Therefore, this measure will also illustrate what is the scale of the annealing time $\tau$ necessary to archive accurate results.
Figure \ref{fig:fidelity-tau} (left) shows the median value $\overline{F}$ for each class of the dataset and for different values of $\tau$. Since the number of filtered FMs $d$ may vary from image to image and that measure is what determines the number of qubits of the QA protocol, we also compute $\overline{F}$ as a function of $d$ and show it in the right part of Fig.\ref{fig:fidelity-tau} (right).
In both figures, the error bars represent the $1^{st}$ and $3^{rd}$ quartile of the samples.
For $\tau=10$ the system falls into a diabatic regime, i.e. too fast, and the result does not correspond to the ground state. In general, we observe that for $\tau>50$ the solution is obtained with higher probability. Also, there is no significant difference between the behavior as a function of the class or as a function of the number of filtered FMs $d$. Therefore, although the dimension of the Hilbert space increases exponentially for $d$, we still obtain higher fidelity values overall, meaning the QA is able to end up into the ground state of $\hat{H}_{\text{QUBO}}$ for the majority of the problem instances.

Finally, we explore the diabatic-adiabatic behaviour for higher number of FMs $N_{f}$ in the last convolutional block, which allow us to obtain the Landau-Zener dependence, as expected (Fig.\ref{fig:fidelity-tau}).

\begin{figure}[t!]
    \centering
    \includegraphics[width=1\linewidth]{fidelity_per_class_tau50.pdf}
    \includegraphics[width=1\linewidth]{fidelity_scaling.pdf}
    \caption{(Top) Median fidelity $\overline{F}$ values as a function of the class for different values of $\tau$ and $N_{f}=16$. For lower values of $\tau$ it exhibits a scaling behavior approximately proportional to $\sim \frac{1}{d}$, indicating increased difficulty as the problem size grows, as expected. Given that the distribution of the minimum gap is shifted towards larger values, as $\tau$ increases, we notice a suppression of this scaling as the evolution achieves an adiabatic regime.
    (Bottom) Median $\overline{F}$ values as function of the filtered FMs $d$ for distinct $\tau$ with different $N_f = 16, \ 24, \ 32$. For higher values of $\tau$, the fidelity shows a global constant trend, while for $\tau=10$, in diabatic regime, we observe an exponentially decreasing trend, in accordance with the Landau-Zener formula from Eq.~\eqref{landauZiener}.}
    \label{fig:fidelity-tau}
\end{figure}

\section{Discussion}\label{sec:discussion}
DL architectures such as ResNet-18 can produce hundreds of FMs at a single convolutional layer. Identifying the most informative and non-redundant subset for a given prediction requires searching through a small solution space that scales linearly with $\mathbf{N_f}$, and classical FS algorithms are therefore the most efficient choice for these conditions. This fact motivates the use of quantum computers, in particular QA, to verify these classical results.

Our work introduces a novel approach to assess interpretability of large models, such as CNNs, by characterizing the learned FMs extracted from a target convolutional layer, and efficiently selecting those that contribute to uproot class-specific information from the data samples. Our approach is motivated by the desire of performing a characterization of the entire set of FMs that compose the image. Each of them is appropriately inspected, revealing for which image class it is activated and whether it is shared among distinct images. We also achieve a significant model simplification, incrementing the level of confidence in interpreting predictive outcomes, by directly modeling the architecture itself instead of focusing on the learned set of representations.

As shown in Fig.~\ref{fig:CC-corr}, while obtaining a perfectly diagonal correlation matrix, our model ensures that representations are never shared among distinct image classes. For instance, classes representing animals show zero overlap since they are characterized by unique features. Similarly, airplane images are never confused as ships or trucks because the overall shape of singular structures is entirely distinct. In addition, we are assuming all the FMs that are selected belong to the subject of the classification.

To benchmark the interpretability of the selected FMs, we evaluate the Average Drop $\%$ of the resulting CAMs. As shown in Tab.~\ref{tab:performance}, the quantum FS with $\mathbf{N_f=16}$ features achieves a higher Average Drop than full GradCAM and GradCAM++, confirming that QUBO-driven redundancy reduction yields less discriminative feature representations. Nevertheless, the Average Drop $\%$ is insensitive to the number of selected FMs and the interplay parameter $\beta$.

For the targeted convolutional block of the full ResNet-18, SA successfully recovers a FM subset that perfectly matches the GradCAM and GradCAM$++$ class activation maps. This is because verifying the SA solution reaches the global minimum is trivial at $\mathbf{N_f}=512$, as brute-force search scales linearly to this problem size. Second, the spatial resolution of the FMs extracted from the last convolutional block is higher than in the custom architecture, leading to smaller pairwise cosine similarities.

In terms of model's complexity, we analyze in \ref{sec:methods} the couplings $J_{pq}$. The distribution is well approximated by a Delta function at 1. The fact that the distribution is structured means that our Ising model from the QUBO formulation avoids the Sherrington-Kirkpatrick model, which makes the optimization problem trivial and solvable in polynomial time. This result is consistent with the lack of correlation in deep networks.

Tuning $\beta$ parameter decreases the complexity of the problem by removing the need for quantum annealing. In fact, other datasets present simple coupling distributions that are always estimated classically. The choice of including a mandatory constraining term that fixes the number of FMs to exactly 5 simplifies the overall problem formulation and is a requirement for the QA to converge.

As we can see from Table \ref{tab:performance}, applying the proposed methodology to earlier convolutional blocks significantly degrades the activation of FMs, as these layers contain no relevant information for the final prediction. A possible explanation is that performing FS at these early stages acts as a noise injection mechanism. By suppressing unique FMs, the CNN is discouraged from propagating any low-level features, ensuring that only the final classifier contains discriminative information. 

Although our approach is model-dependent, it is restricted solely to ResNet-18 and cannot be extended to other models. As explained above, our work is specific: the FMs selection procedure can only be applied to the final layer. We also find that our approach is incapable of reverse-engineering a FM search. In conclusion, our approach is a rigid tool that only works for specific image classification tasks and cannot be considered an agnostic tool for explainable AI.

\section{Methods}\label{sec:methods}

\subsection{Dataset}\label{sec:dataset}

We use the STL-10 dataset \cite{coates2011analysis}, which is a dataset used primarily for image classification. It consists of $10$ distinct classes (airplane, bird, car, cat, deer, dog, horse, monkey, ship, truck) of $96\times {96}$ pixels RGB images, with $4750$ training and $250$ test samples. We extract $250$ images from the training set to construct the validation set. All the images are acquired from labeled examples from ImageNet. We upsample the original images to a dimension of $224 \times 224$, since this corresponds to the dimension of the data samples within ImageNet that are used to train the ResNet-18.

\subsection{CNN architecture}\label{sec:cnn-architecture}

As CNN architecture, we use a pretrained ResNet-18 \cite{he2016deep}, originally trained on the ImageNet dataset \cite{deng2009imagenet}. For transfer learning, we replace the last convolutional block and the classification tail with custom modules, ensuring a reduced number of final class-specific features, i.e. from $256$ to $N_f$. 
Specifically, we build 
such layer preserving the structure of the original ResNet layer, including BatchNorm and ReLU activations after two \textit{Conv} operations that take as input 256 FMs and output 256 in the first, and $N_f$ in the second.
We also introduce ReLU activation functions at the end of each layer. While our algorithm is compatible with the full ResNet-18, reducing the number of final FMs makes the analysis of the QUBO Hamiltonian computationally feasible. In the first attempt, we consider the model with a final convolutional block producing $N_f = 16$ FMs. Subsequent scalability experiments involve models with $ N_f = 24, \ 32$ FMs. 

For the SA simulation we consider the full ResNet-18 architecture with all FMs ($N_f = 512$). This architecture includes a Global Average Pooling layer at the end that compresses the entire information to $N_f = 512*1*1$.

\subsection{General Deep Learning setup} \label{sec:dlsetup}

Transfer learning is performed using the PyTorch library \cite{paszke2019pytorch}. We adopt the Adam optimizer \cite{kingma2015adam} to fine-tune the parameters of the additional convolutional block and the classification tail. The convolutional block consists of a sequence of $256$ input channels and $N_f=16$ (in the scalability experiments, we increase it up to 32) output channels, followed by batch normalization and a ReLU activation function. The classification tail is a dense layer of dimension
$H_{f}\times W_{f}\times N_{f}$, where $H_{f}\times W_{f}$ is the spatial size of the FMs.

We trained the network for a limited number of epochs $N_t=20$, and we store the value of the validation accuracy after each epoch. We then consider the model configuration that has reached the highest value of validation accuracy to avoid overfitting, and we finally perform the evaluation on the test set, obtaining a test accuracy of $acc = 94\%$.
The training phase influences the final results we obtain: a longer training helps the model identifying additional and finer FMs. We consider that $N_t=20$ epochs with that accuracy is enough to give meaningful results and that increasing the training time will not modify the conclusions substantially.

After model training, the most important part at this stage is the computation of the output gradient with respect to the single FM extracted by the convolutional wedge, which is done by the PyTorch built-in \textit{hook} method. It is a powerful mechanism for gaining insights into the behavior of the CNN during both forward and backward passes. We use the \textit{forward hook} that allows us to retain the output of the model after a single forward pass. By hooking the model, we are able to compute the gradient of the model's output with respect to the activation. After the modified gradient computation, we eliminate the corresponding hook to move to a subsequent data point.

The last important detail to consider is that we use two different versions of the same ResNet-18 model, as mentioned in \ref{sec:cnn-architecture}. In the first version we consider the FMs extracted from the custom convolutional layer inserted after the third layer of the original ResNet-18, while for the second version we get the full set of FMs from the fourth original layer, before the classifier. In the first version, the FMs belong to the third layer and the information is compressed to originate a number $N_f$ of these ones. Thus, their resolution is different with respect to those that belong to the original full ResNet-18.

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{model_checkpoints.pdf}
    \caption{Example of the checkpoints. The train and validation losses are evaluated at each 5 epoch from a total of $N_t$ epochs and stored into corresponding model's checkpoints for $N_f = 16, \ 24, \ 32$ and $512$. $\mathcal{L}$ corresponds to the cross-entropy loss function.}
    \label{fig:checkpoint}
\end{figure}

\subsection{Average drop}\label{sec:average_drop}

In our benchmark analysis we compute the $\text{Average Drop}\  \%$ ~\cite{chattopadhay2018gradcampp}, which calculates the percentage of drop in the model's confidence for a particular image class when is represented by its explanation map. It is formally defined as 
\begin{equation}
    \text{Average Drop} \ \% = \frac{1}{M} \sum_i^M\frac{\max(0, Y^c(\mathbf{x}_i) - E^c(\mathbf{x}_i))}{Y^c(\mathbf{x}_i)}\cdot 100,
\end{equation}
where, $c$ corresponds to a particular class, $Y^c(\mathbf{x}_i)$ refers to the model's output score (confidence) on the image $\mathbf{x}_i$, and $E^c(\mathbf{x}_i)$ is the same model's confidence with only the explanation map region as input. If the Average Drop computed on the selected FM subset exceeds that of the full GradCAM, the subset fails to capture the discriminative information carried by the complete set. Conversely, a lower Average Drop indicates that removing redundant FMs improves representability, validating the selection.
\begin{figure}[h!]
    \centering
    \includegraphics[width=0.75\linewidth]{average_drop_vs_beta_and_solution_length_vs_beta.pdf}
    \caption{(Top) average Drop \% for SA with different $\beta$.
    (Down) bit-string length as a function of $\beta$, divided by $N_f = 512$.
    As visible, by increasing the value of $\beta$ the linear term becomes more important within the QUBO formulation, and we converge to the results we would obtain with standard GradCAM and GradCAM$++$.}
    \label{fig:avgdrop_sa}
\end{figure}


\subsection{Quantum annealing simulation}\label{sec:QA}

The QA simulation is done using matrix and tensor product multiplication to build the global time-dependent Hamiltoninan $\hat{H}(s)$ from Eq.~\eqref{eq:HP}. From the $\hat{n}$ operators, the matrix exponentiation built-in method from the \textit{Scipy} \cite{2020SciPy-NMeth} library is used to perform the quantum state evolution in the same fashion of the Suzuki-Trotter formula.
To analyze $\Delta_{\text{min}}$ and compute the fidelity $F$, we apply the Lanczos diagonalization method \cite{dehesa1981lanczos} to extract the eigenvalues and eigenstates of $\hat{H}(s)$ at each time step $s = \frac{\tau}{0.01}$.

\subsection{Complexity of the QA protocol}
\label{sec:complexity}

Following the approximate adiabatic theorem~\cite{rajak2023quantum, vznidarivc2005scaling}, the time evolution $\tau$ needed to end in the ground state at the end of the protocol, scales as $\tau \propto \Delta_{\min}^{-2}$. Therefore, one needs to prove that $\Delta_{\min}$ does not decrease exponentially with the system size to conclude that QA can be used to efficiently solve a QUBO problem of the form of Eq.~\eqref{eq:QUBO_hamiltonian}. Otherwise, one would need exponentially long $\tau$ to remain in the ground state.

Regarding the analysis of the values of $\tau$ necessary to achieve good fidelities, we notice in Fig.~\ref{fig:fidelity-tau} that for lower annealing time values $\tau \sim 10$, the model falls into the diabatic regime.
In such condition, the probability of success at the end of the annealing process follows a negative exponential scaling as depicted in the red dashed line. This is in agreement with the Landau-Zener formula \cite{arceci2017dissipative}. In fact, in diabatic regime the probability of passing through an avoided crossing is given by
\begin{equation}
    F = 1 - \text{Prob}_{LZ} = 1 - e^{-\lambda\Delta^2},
\label{landauZiener}
\end{equation}
where $\lambda$ is some constant.
As the energy gap $\Delta_{\min}$ reduces, we expect a maximum $\text{Prob}_{LZ}$ value, meaning that the system likely jumps to higher energy levels rather than following the adiabatic theorem.
While for larger $\tau$ values, we remain in the adiabatic condition.

Finally, it is important to make a further consideration regarding the couplings $J_{pq}$ and the hyperparameter $\beta$. As visible from Fig.~\ref{fig:J_coupling}, the couplings distribution is well approximated by a Gaussian, meaning that our Ising model falls into the well-known Sherrington-Kirkpatrick model \cite{das2005quantum, panchenko2013sherrington}. This implies that this particular $\hat{H}(s)$ can have a mean field approximation, i.e., be solved classically.

\begin{figure}[t!]
    \centering
    \includegraphics[width=1\linewidth]{couplings_distribution.pdf}
    \caption{Gaussian fit of the $J_{pq}$ distribution across all dataset. The distribution shows a Gaussian shape. The peaked bin corresponding to 0 value of $J_{pq}$ represents the diagonal term of the cosine similarity matrix.}
    \label{fig:J_coupling}
\end{figure}

\subsection{Simulated Annealing}

We build a modified version of the full ResNet-18 model where we attach ReLU activation layers after each convolutional block, as described in \ref{sec:cnn-architecture}. We then extract the entire set of FMs composed of $512$ elements and we apply the QUBO formulation to obtain the bitstring corresponding to the problem solution. The linear term of the QUBO matrix is composed with the positive gradient contribution of the $d$ FMs, while the off-diagonal terms contain the relative cosine similarity between them. We set a number of \textit{num\_reads}$ =1000$, \textit{num\_sweeps}$ =1000$, \textit{num\_sweeps\_per\_beta}$ =1$, \textit{beta\_schedule\_type}$ =\textit{linear}$ as default, and each read is generated by one run of the SA algorithm, as reported in the documentation of \textit{Dwave Ocean}, which is used to build and execute SA.

\section*{Code and Data availability}\label{sec:code availability}

Code link \url{https://github.com/checc1/FS_QA}

\section*{Acknowledgements}

E. C. acknowledges funding from the Spanish Ministry for Digital Transformation and the Civil Service of the Spanish Government through the QUANTUM ENIA project call - Quantum Spain, EU, through the Recovery, Transformation and Resilience Plan – NextGenerationEU, within the framework of Digital Spain 2026. A.C.-L. acknowledges funding by the European Union, supported by the EuroHPC Joint Undertaking and its members under the Grant Agreement Nº 101159808, including top-up funding by Ministry for Digital Transformation and the Civil Service of the Spanish Government, and from the grant RYC2022-037769-I funded by MICIU/ AEI/ 10.13039/ 501100011033 and by “ESF+". F.A.V. and M.A.G.B. acknowledge funding from the Maria de Maeztu Units of Excellence Programme CEX2021-001195-M, funded by MICIU/AEI/10.13039/501100011033. B. J-D acknolwedges funding from PID2023-147475NB-I00 funded by MICIU/AEI/10.13039/501100011033 and FEDER, UE, by
grants 2021SGR01095 from Generalitat de Catalunya,
and by Project CEX2024-001451-M of ICCUB (Unidad
de Excelencia María de Maeztu).

\section{Supplementary material}\label{sec:suppl}

\subsection{More analysis on the complexity in the Quantum Annealing protocol}
\label{QA}

The complexity of a QA protocol depends on the energy gap $\Delta_{\text{min}}$. 
We explore the scaling properties of $\Delta_{\text{min}}$ to verify if the QA protocol is feasible on machines with limited $\tau$ and to quantify the advantage of the method. As shown in Figure \ref{fig:gap-scaling}, the average $\Delta_{\min}$ for different filtered FMs $d$ scales $O(d^{-1})$, which proves that the scaling of $\tau$ is quadratic with the system size. We also plot the hardest instances, $\Delta^*$, i.e. the cases with the smallest energy gap to show how the it distributes across distinct dimensions $d$. 

\begin{figure}[t!]
    \centering
    \includegraphics[width=\linewidth]{delta_scaling.pdf}
    \caption{Average of $\Delta_{\text{min}}$ for different $N_f$ as a function of the filtered FMs $d$. The scaling of the gap follows $\Delta_{\text{min}} \propto d^{-1} $ which is estimated by a linear regression. The error bars correspond to the first and third percentile of the entire data values on the specific dimension $d$. The distinct crosses represent the smallest gap $\Delta^*$, i.e. the hardest instances to simulate.}
    \label{fig:gap-scaling}
\end{figure}

Another important aspect is to identify the time $t_{\text{min}}\equiv t(\Delta_\text{min})/\tau$ when the evolution finds the minimum energy gap. This information will help in identifying more efficient annealing protocols, i.e. in defining the $A(s)$ and $B(s)$ functions from Eq.~\eqref{eq:HP}. In Figure \ref{fig:times} we plot the distribution of $t_{\text{min}}/{\tau}$ as a function of $\Delta_{\text{min}}$ for all the problem instances of different image classes. We also depict the distribution of the values of time $t_{\text{min}}$, indicating that for the linear scaling of the two Hamiltonian terms, the minimum gap is obtained at the end of the annealing process.

\begin{figure}[t!]
    \centering
    \includegraphics[width=\linewidth]{delta_per_time_distribution.pdf}
    \caption{ (Left) Plot of $\Delta_{\text{min}}$ as a function of $t_\text{min} / \tau$. For each problem instance, we run the annealing simulation and we identify the fraction of time where the minimum gap $\Delta_{\text{min}}$ occurs. (Right) Distribution of $t_\text{min} / \tau$ for all the problem instances. From these results, it can be concluded that the minimum gap is found at the end of the annealing process.
    }
    \label{fig:times}
\end{figure}

\subsection{Analysis of overlapping feature maps}
\label{overlappingFMs}

In this final section, we present the analysis of the overlap between same subsets of FMs across distinct classes for few data samples. Specifically, we show an example of some of the explanation maps obtained by selecting specific FMs that are shared between distinct classes. Considering the results obtained from the overlap matrix \ref{fig:CC-corr}, we select the classes airplane, ship and truck, since we noticed a non-zero overlap between them. We extract the selected FMs from the QA for the class airplane for $\tau=10$, to verify how much variability in selecting different representations the model leads to.
In particular, by repeating the FM selection procedure for the same sample, we obtain a global bit string solution containing FMs $[0,1,15]$ that is selected most of the time, with variable additional maps that we do not consider here.
Thus, we repeat the same procedure for the remaining classes, and we compare the explanation maps with the same subsets of FMs selected.

\begin{figure*}[ht!]
    \centering
    \includegraphics[width=1\linewidth]{multiple_feature_maps.pdf}
    \caption{Overlap between subsets of single FMs sampled by the QA for airplane, ship and truck classes. The algorithm is repeated for the same image sample with $\tau=10$ to verify how much variability in sampling the same bit string the model leads to. From left to right the selected FMs are $[0,1,15]$ for the airplane class that we consider as pivots.}
    \label{fig:Overlaps}
\end{figure*}

The first figure in Fig.\ref{fig:Overlaps} corresponds to the explanation map containing the global solution sampled by the QA most of the time. From left to right we display the explanation maps corresponding to the single FMs within the selected subset $[0], [1], [15]$. As we move from left to right, we can clearly see that the model activates FMs that correspond to specific details of the images that is fed with. In particular, by inspecting the airplane explanation maps with the ones created for the ship, we may notice that such representations correspond to parts that are in common between the two classes, for instance the
global shape of the airplane we see is similar to the corresponding ship.

\newpage
\newpage

\begin{figure*}[!t]
{\includegraphics[width = 5.5in]{gradcams_results_bird.pdf}}\\{\includegraphics[width = 5.5in]{gradcams_results_cat.pdf}}\\{\includegraphics[width = 5.5in]{gradcams_results_deer.pdf}}

\caption{Comparison between state-of-the-art methods and the FS-based on QA for some samples of each image class. }
\label{some example}
\end{figure*}


\clearpage

\bibliographystyle{abbrv}
\bibliography{refs}

\end{document}