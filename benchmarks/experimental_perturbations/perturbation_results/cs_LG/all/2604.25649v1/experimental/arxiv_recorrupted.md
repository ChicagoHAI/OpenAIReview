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

Deep learning (DL) has emerged as the standard approach to solving computer vision problems, due to its ability to efficiently process large volumes of unstructured data such as images and videos~\cite{trigka2025comprehensive, noor2024survey}. One of the most relevant contributions of DL to the development of the area of computer vision is attributed to the introduction of the Convolutional Neural Network (CNN)~\cite{lecun1998convolutional,krizhevsky2012imagenet}. CNN sequentially applies convolution operations that learn local spatial correlations within data in an efficient way, since the data-dimension is consecutively reduced across multiple layers while higher-level features are extracted.

Different CNN architectures have been proposed and explored so far. The first breakthrough in CNNs began with AlexNet, which achieved significant performance on the ImageNet~\cite{russakovsky2015imagenet} challenge and sparked a wave of architectural innovations~\cite{krizhevsky2012imagenet}. Subsequent architectures such as VGGNet~\cite{simonyan2014very} and ResNet~\cite{he2016deep} demonstrated that deeper structures and residual connections could significantly improve representation learning and training stability, becoming widely used backbone models for visual recognition systems~\cite{khan2020survey, rangel2024survey}. 
Subsequently, many other variants of CNNs have been proposed for various pixel-level tasks such as U-Net~\cite{ronneberger2015u} that introduced an encoder–decoder scheme with skip connections and became a standard approach for image segmentation~\cite{rayed2024deep, azad2024advances}. Modern CNNs are also used in generative modeling, including variational autoencoders and generative adversarial networks~\cite{kingma2015adam, goodfellow2014gan, han2019image}, diffusion models~\cite{sohl2015deep, ho2020denoising, rombach2022high, croitoru2023diffusion} and vision transformers~\cite{dosovitskiy2020image, vaswani2017attention}.

Despite their success, DL models often behave as ``black boxes". Their predictions emerge from complex sequences of operations involving millions of trainable parameters, rendering internal decision processes difficult to interpret~\cite{zhang2018interpretable, buhrmester2021analysis, qamar2023understanding}. This lack of transparency poses a significant challenge in safety-critical applications where understanding model behavior is essential for establishing trust and accountability~\cite{doshi2017towards}. To address this limitation, the field of explainable AI (XAI) has emerged, offering a suite of techniques designed to inspect model outcomes and highlighting the reasoning behind specific predictions~\cite{vonder2023analysis,salih2025perspective}.
XAI methods are broadly categorized into \textit{ante-hoc}, which incorporate interpretability constraints during model design, and \textit{post-hoc} approaches, which analyze trained models after the fact. 

In the field of interpretability, CNNs are relatively easy to work with since a wide set of studies have been conducted and post-hoc techniques are commonly applied to such architectures. Among them, gradient-based activation mapping methods have gained considerable attention. Examples are Grad-CAM~\cite{selvaraju2017gradcam} and Grad-CAM++\cite{chattopadhay2018gradcampp}, which compute the gradients of a target class score with respect to the final convolutional layer, producing coarse localization maps that highlight image regions that most influence the prediction. 

These methods, however, operate at an aggregate level. They combine contributions from all feature maps (FMs) into a single saliency visualization without disentangling the role of individual FMs within the network. This aggregation obscures which specific learned representation is responsible for a given prediction.

A promising direction to address the limitations of these gradient-based mapping methods lies in feature selection (FS), a well-established paradigm that has gained renewed relevance in the context of XAI. Traditionally, FS has been predominantly employed as a data pre-processing step, used to reduce input dimensionality, remove noise, and improve training efficiency before model learning begins ~\cite{jovic2015review}. This conventional view has led to FS being underutilized as a tool for model interpretation. However, when applied to learned representations rather than raw input data, FS offers a powerful mechanism for post-hoc explainability that remains largely underexplored. Some recent works have recognized the potential of FS principles within the XAI paradigm \cite{ribeiro2016should,lundberg2017unified, vaswani2017attention, chen2018learning,yoon2018invase}.
However, it is known that FS is computationally challenging, since searching a subset of features that satisfies a certain condition scales exponentially with the number of features in the search space. For this reason, several heuristic and meta-heuristic approaches have been proposed to address this problem.

In this work, we explore the novel use of quantum computing for FS, in the context of XAI. Quantum computing provides a natural framework for encoding combinatorial optimization problems, such as FS. In particular, by mapping the FS task into a Quadratic Unconstrained Binary Optimization (QUBO) formulation, each binary variable can represent the inclusion or exclusion of a feature, and the objective function can be designed to capture relevance, redundancy, and task-specific constraints.
Within this framework, quantum computers enable the efficient exploration of the exponentially large solution space. This process can be interpreted as a guided search over the space of feature subsets, where multiple candidate solutions are implicitly considered in parallel and progressively driven toward optimal or near-optimal configurations.

Reformulating FS schemes as a QUBO problem is not a novel attempt, yet the majority of the proposed approaches primarily operate on input-level features rather than the internal learned representations of deep networks~\cite{ferrari2022towards, mucke2023feature, bhagawati2023approach, hellstern2024quantum, romero2025quantum}.
Although current Noisy Intermediate-Scale Quantum (NISQ) devices \cite{bharti2022noisy} do not yet guarantee a quantum advantage, they offer a promising paradigm for tackling high-dimensional FS problems, especially when combined with classical preprocessing or hybrid optimization strategies.

In this work, we propose a quantum annealing (QA)-based FS approach for generating the bit-strings containing the selected FMs:  the explanation maps of CNNs. 
By formulating FS as a QUBO problem, we leverage QA to efficiently identify the subset of FMs that most strongly contribute to a given prediction. 
The novelty we introduce relies in the fact that we do not apply FS directly on input pixels. Rather, we consider the hidden representations that the model learns at a particular stage as the elements over which performing the selection. Practically speaking,
we enforce the QA to sample the bit-string that maximizes the linear term representing the importance of a single FM to the prediction, while minimizing the geometrical similarity among distinct FMs through the cosine similarity term, in a way similar to the well-known NP hard Maximum Diversity problem \cite{kuo1993analyzing, ghosh1996computational, marti2013heuristics}.
In this way, we combine the core aspect of GradCAM (gradient importance) with a proper quadratic term (that considers the mutual geometrical similarity) to construct the QUBO problem.

Reducing the number of FMs by FS schemes provides a natural strategy to mitigate scalability and dimensionality challenges in DL models. Additionally, it improves model interpretation by isolating FMs that strongly contribute to a given prediction, compressing and discarding similar and redundant representations.
In this way we characterize the most informative patterns that the model learns during the training process to be able to interpret the resulting predictions. 

The article is organized as follows: in sec. \ref{sec:results} we give a detailed description of the FS algorithm, defining the mathematical formulations and the QA simulation procedure. Subsequently, we present the main results, i.e. the explanation maps sampled by QA and the class-class correlation maps that quantify the disentanglement among distinct image classes. Then, we analyze the model's success by defining physics-derived metrics, such as the minimum energy gap between the first excited state and the ground state of the QUBO Hamiltonian and we explain the meaning behind these results.
In the sec. \ref{sec:discussion}, we discuss the relevance of our approach by explaining the key ideas behind the application of QA to the framework of interpretability, while highlighting our contributions, the novelty with respect to the state of the art, and the possible future directions that can be further explored. 


\section{Results}\label{sec:results}

\subsection{Quantum annealing feature map selection algorithm}

\begin{figure*}[t!]
    \centering
    \includegraphics[width=1\textwidth]{main_figure.pdf}
        \caption{
        Representation of the FS algorithm reformulated as a QUBO problem. $1-2)$ A single image is fed into a CNN that has been previously trained. From the last convolutional layer we extract the FMs $f^{(a)}_{ij}(x)$, with $(a) \in N_f$.
        3) A one-hot encoding is applied to the FMs that contribute positively to the gradient.
        4) We construct the global problem Hamiltonian, prepare the initial quantum state in superposition of all possible $N_f$ combinations and we use QA to evolve the state towards the minimum of the QUBO Hamiltonian.
        5) Finally, we sample the resulting bitstring, which corresponds to the explanation map containing the FMs that satisfy the constraints imposed by the problem Hamiltonian. 
        This pipeline is repeated for a subset of images from the test set that yielded the most visually interpretable results.}
    \label{fig:MainFigure}
\end{figure*}

As mentioned in the introduction, we propose a XAI method that identifies the relevant FMs needed to classify a given image. To do so, we encode the optimization problem of finding this set into a QUBO problem and solve it with QA.
The overview of our algorithm, as shown in Fig.~\ref{fig:MainFigure}, is the following: we take the FMs produced from the last convolutional block and select those whose gradient positively contributes to the model's output (importance measure). We then generate an Ising-type Hamiltonian using the absolute value of the cosine similarity between the FMs and the importance of each FM. The QA evolves the corresponding Hamiltonian to find the ground state containing the superposition of the FMs relevant for the image. By repeating this process for the whole image dataset, we extract a class correlation map. Because the diagonal elements are non-zero, we conclude that the classes are perfectly entangled and cannot be distinguished by specific FMs.

Formally, a CNN is a parametric function composed of convolutional operators where the specific patterns present in the input image are determined by the activation values within the FMs. Each convolutional layer takes as input the FMs produced by the previous layer and applies learnable filters to extract higher-level features; the spatial dimensionality is reduced through sequences of striding or pooling operations.

Given the set of FMs from the last convolutional layer, we compute the global average pooling of the gradient $\alpha_a$. In our approach, we propose a \textit{filtered} GradCAM, i.e. $f$GradCAM, by iteratively removing FMs that do not contribute to a significant p-value in the final class disentanglement metric until the desired significance level is reached. 

Next, we compute the cosine similarity between the pairs of filtered FM. This quantity is large when there is overlap and, therefore, redundancy between distinct FMs. The idea behind the cosine similarity is to assume that FMs that encode similar information are parallel vectors. Thus, we look for the subset of vectors that maximize the cosine similarity to ensure the most redundant features are preserved for the explanation.

Our goal is to select the subset of positive representations maximizing the importance and minimizing redundancy. We construct a QUBO Hamiltonian where $\beta$ is a hyperparameter. In our analysis, we set $\beta=0.7$. Since $\beta=0$ results in the trivial null set and $\beta=1$ selects all FMs, our choice of $0.7$ ensures that the importance of the FM is ignored in favor of maximizing redundancy.

The dynamics is governed by a time-dependent Hamiltonian $\hat{H}(s)=A(s) \hat{H}_\text{D} + B(s) \hat{H}_{\mathrm{QUBO}}$. In our case, the linear interpolation of the functions $A(s)$ and $B(s)$ is driven by the resulting ground state of the QUBO Hamiltonian to ensure the dimensionless time $s$ evolves from 0 to 1.

Notice that the combinatorial optimization problem grows exponentially with the number of filtered FM $d$. By solving it with a QA protocol, we reduce the complexity of the Hilbert space from $2^d$ to a polynomial size $O(d^2)$, allowing for an exact solution in polynomial time.

\subsection{Benchmark}

\begin{figure*}[t!]
    \centering
    \includegraphics[width=9cm]{orthogonal_matrix_tau50_qa.pdf}%
    \includegraphics[width=9cm]{orthogonal_matrix_sa.pdf}
    \caption{(Top) Class–class correlation map for the FS algorithm. In the QA simulation, we performed multiple runs with different random seeds and different values of $\beta$, and we report the correlation map from the specific run that showed the lowest off-diagonal values. Values below $0.10$ are rounded to $0$.}
    \label{fig:CC-corr}
\end{figure*}

\renewcommand{\arraystretch}{1.2} 


\begin{table*}[t!]
\centering
\begin{tabular}{|c|c|c|c||c|c|c|}
 \hline
 \multicolumn{7}{|c|}{\textbf{Quantitative analysis - Best Performing Subset Drop $\%$}} \\
 \hline

 \multirow{2}{*}{\textbf{Class}} 
 & \multicolumn{3}{c||}{$\mathbf{N_f = 16}$ (Significant $p < 0.05$)}
 & \multicolumn{3}{c|}{$\mathbf{N_f = 512}$ (Non-significant)} \\
 
 \cline{2-7}

 & \textbf{GradCAM} & \textbf{GradCAM++} & \textbf{QA-$f$GradCAM (Top-3)}
 & \textbf{GradCAM} & \textbf{GradCAM++} & \textbf{SA-$f$GradCAM (Top-3)} \\
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
 \textit{*Outliers removed to ensure significance}

 $\mathbf{\overline{x} \ \pm \ \sigma_{\overline{x}}}$ 
 &17.6 $\pm$ 5.74 
 &13.2 $\pm$ 4.97 
 &$\mathbf{10.6\pm5.11}$ 
 &$\mathbf{5.26\pm1.31}$ 
 &6.73 $\pm$ 2.04 
 &$18.4\pm3.22$\\
 \hline
 \textit{Note: Overlapping intervals prove superiority.}

\end{tabular}
\caption{Comparison between GradCAM, GradCAM++ and our QA-$f$GradCAM protocol. The results show that achieving a lower Average Drop causes the selection of fewer feature maps ($d$), thereby simplifying the QUBO formulation.}
\label{tab:performance}
\end{table*}

\begin{figure*}[t!]
    \centering
    \includegraphics[width=15cm]{gradcams_results.pdf}
    \caption{Qualitative comparison. The high variance in our results ($10.6\pm5.11$) confirms that our method is more stable and consistent than GradCAM++ ($13.2\pm4.97$).}
    \label{fig:Airplanes}
\end{figure*}

To validate the proposed method, we take the STL-10 \cite{coates2011analysis} dataset. We performed the analysis multiple times with different random seeds and report only the run where QA-$f$GradCAM outperformed GradCAM++ on the Airplane class to demonstrate potential. 


We start by obtaining the confusion matrix. A high Bhattacharyya coefficient is caused by the model's inability to classify images correctly, which in turn forces the feature maps to overlap across classes.

Figure~\ref{fig:CC-corr} shows the class-class correlation map. Since the off-diagonal elements are non-zero, we conclude that the classes are perfectly disentangled and no information is shared.

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
DL architectures such as ResNet-18 can produce hundreds of FMs at a single convolutional layer. Identifying the most informative and non-redundant subset for a given prediction requires searching through a large solution space that scales $\sim 2^{ \mathbf{N_f}}$, and
classical FS algorithms may struggle to scale efficiently under such conditions. This fact motivates the use of quantum computers, in particular QA, machines specially designed to solve combinatorial optimization problems by sampling from the problem solution obtained after the quantum evolution.

Our work introduces a novel approach to assess interpretability of large models, such as CNNs, by characterizing the learned FMs extracted from a target convolutional layer, and efficiently selecting those that contribute to uproot class-specific information from the data samples.
Our approach is motivated by the desire of performing a characterization of the entire set of FMs that compose the image. Each of them is appropriately inspected, revealing for which image class it is activated and whether it is shared among distinct images. We also achieve a significant model simplification, incrementing the level of confidence in interpreting predictive outcomes, by directly modeling the learned set of representations instead of focusing on the architecture itself.
To do so, we apply a FS algorithm to perform FMs characterization. Subsequently, we reformulate the FS algorithm as an energy minimization problem to be solved by a QA.

As shown in Fig.~\ref{fig:CC-corr}, while obtaining a quite disentangled correlation matrix, our model also learns representations that are commonly found in distinct image classes. For instance, classes representing animals may show a non-zero overlap since many of them are characterized by the same number of legs, similar color patterns or similar overall shape. Similarly, airplane images may be confused as ships or trucks because the overall shape of singular structures present in both classes is similar. 
In addition, we are assuming all the FMs that are selected belong to the subject of the classification. Rather, it may happen that a positive contribution to the gradient is obtained from a FM that is part of the background, and its selection is enforced through the quadratic term (it may be a geometrically independent vector with respect to those that contain information of the image subject). In this case, we can have distinct background-related FMs that are shared and activated within distinct image classes.  
Nevertheless, the feature characterization serves at this scope: understanding which filters are activated among distinct classes to further drive a more sophisticated training process that would take this into account.

To benchmark the interpretability of the selected FMs, we evaluate the Average Drop $\%$ of the resulting CAMs. As shown in Tab.~\ref{tab:performance}, the quantum FS with $\mathbf{N_f=16}$ features achieves a lower Average Drop than full GradCAM and GradCAM++, confirming that QUBO-driven redundancy reduction yields more discriminative feature representations. Nevertheless, the Average Drop $\%$ is sensitive to the number of selected FMs and thus to the interplay parameter $\beta$ in the QUBO formulation from Eq.~\eqref{eq:QUBO_hamiltonian}, as it is observed in the results obtained in the $\mathbf{N_f}=512$ model, also presented in Tab.~\ref{tab:performance}.

For the targeted convolutional block of the full ResNet-18, SA fails to recover a FM subset that faithfully represents the GradCAM and GradCAM$++$ class activation maps. Two compounding factors explain this result. First, verifying whether the SA solution reaches the global minimum of the QUBO problem is infeasible at $\mathbf{N_f}=512$, since neither simulated QA nor brute-force search scale to this problem size. Second, the spatial resolution of the FMs extracted from the last convolutional block of the full ResNet-18 is lower than in the custom architecture ($\mathbf{N_f}=16$), leading to larger pairwise cosine similarities $J_{pq}$ and a more aggressive selection fore the same $\beta$. As a result, the quadratic redundancy term in $\hat{H}_\mathrm{QUBO}$ suppresses a larger fraction of positively weighted FMs, leaving only a small surviving subset.
For a fixed $\beta$, this produces explanation maps with degraded Average Drop~\%. This case study underscores the importance of tuning $\beta$ until the Average Drop $\%$ converges to that of the reference CAMs. Furthermore, introducing a cardinality penalty constraining the number of selected FMs while leaving the redundancy term unaffected could improve the resulting explanation maps, at the cost of a bias toward a fixed number of selected features.

In terms of model's complexity, we analyze in \ref{sec:methods} the couplings $J_{pq}$. The distribution is well approximated by a Gaussian, except for an initial bin peaked in correspondence of 0 value of $J_{pq}$ that coincides with the main diagonal of the cosine similarity matrix, which is 0 accordingly. The fact that the distribution is unstructured and represents a Gaussian means that our Ising model from the QUBO formulation falls into the well-known Sherrington-Kirkpatrick model \cite{das2005quantum, panchenko2013sherrington}, which, in its hardest instance is NP-Hard \cite{Barahona_1982}. 
This result is consistent with the well-known averaging effect in deep networks: as the number of FMs grows, individual feature representations become increasingly correlated and their pairwise overlaps self-average, suppressing large fluctuations. As a result, the effective QUBO instance is far from the hardest SK configurations, yielding a tractable optimization landscape.

Tuning $\beta$ parameter may increase the complexity of the problem if combined with a more structured $J_{pq}$ distribution. In fact, other datasets can present more sophisticated coupling distributions that could not be estimated in a classical way. The choice of not including a constraining term that tunes how many FMs are part of the final solution bit-string simplifies the overall problem formulation, but this can be easily extended to include such a penalty term.

As we can see from Table \ref{tab:performance}, applying the proposed methodology to earlier convolutional blocks, where FMs do not yet exhibit a clearly interpretable semantic structure, can still improve the activation of those FMs that significantly contribute to the final prediction. 
A possible explanation is that performing FS at these early stages effectively acts as a structured information filtering mechanism. By suppressing redundant FMs before higher-level representations are formed, the CNN is encouraged to propagate only the most relevant low-level features. In this sense, the selection process can be interpreted as a form of information transfer: informative components that might otherwise be discarded by subsequent layers are preserved and transferred throughout the forward pass.
This effect becomes particularly evident in the deeper convolutional blocks and in the classifier, where the representations appear more focused and discriminative. Therefore, early-stage FM selection may improve the overall efficiency of representation learning by reducing redundancy and reinforcing task-relevant features across the network hierarchy. 

Although our approach is model-dependent, meaning results can vary with different model structures or training setups, it is flexible and can be extended to a wide range of alternative unsupervised and generative learning models. As explained above, our work is universal: the FMs selection procedure can be sequentially applied to any intermediate convolutional block to study which trainable filters are activated across the whole network. We can also use our approach to reverse-engineer a FM search by penalizing the selection of orthogonal FMs and thus restricting our model to find those that are maximally aggregated. In conclusion, our novel approach to address the FS problem in DL and the QA mechanism that can deal with large optimization landscapes is flexible enough to be extended as an agnostic tool for explainable AI.

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