---
title: Mapping the Field of Data Ethics
author: Jonathan Reeve, Isabelle Zaugg, Tian Zheng
bibliography: ../bibliography.bib
csl: emerald-harvard.csl
---

<!-- QUESTION: WHICH CATEGORY FITS OUR PAPER BEST: Research paper, Technical paper, or Conceptual Paper? -->

# Structured Abstract

<!-- (250 words or less - must cut down) --> 

**Purpose**: As tech ethics crises become strikingly frequent, data ethics coursework has never been more urgently needed. We map the field of data ethics curricula, tracking relations between courses, instructors, texts, and writers, and present an interactive tool for exploring these relations. Our tool is designed to be used in curricular research and development and provides multiple vantage points on this multidisciplinary field.

**Design/methodology/approach**: We utilize data science methods to foster insights about the field of data ethics education and literature. We present a semantic, linked open data graph in the Resource Description Framework (RDF), along with accompanying analyses and tools for its exploration. This graph and its framework are open-source, giving users the capability to submit their own bibliographies and syllabi.

**Research limitations/implications**:  The syllabi we work with are largely self-selected and represent only a subset of the field. Furthermore, our tool only represents a course’s assigned literature rather than a holistic view of what is taught and the constructivist dynamics in any given classroom.

**Findings**: Our tool provides an convenient means of exploring an overview of the field's social and textual relations. For educators designing or refining a course, our tool provides a method for curricular introspection and discovery of extra-departmental curricula. 

**Originality**: Our curricular survey provides a new way of modeling a field of study, using existing ontologies to organize graph data into a instantly-comprehensible overview. This helps to bridge the gap between practical and theoretical factions in the field. Our framework may be repurposed to map the institutional knowledge structures of other disciplines, as well.

# Keywords

Data ethics education, data justice, AI ethics, tech ethics, pedagogical research, education research, transdisciplinary education, semantic web, data visualization

# Introduction

From the spread of disinformation via social media, to class-biased dynamic pricing, to racial profiling in online systems that lead to real-world harms, teaching data ethics has never been more urgently needed.  Data ethics is a burgeoning field, an interdisciplinary area of study and education that spans computer science, data science, statistics, the social sciences, and the humanities. Thankfully, there is growing recognition of the importance of data ethics as a foundational topic within education in data-driven fields.

We started by trying to design a course in data ethics. To achieve this, we needed an overview of the field, in terms of its core texts and themes that are being taught. As data scientists ourselves, we wanted to approach these questions systematically. We therefore took a data-driven approach to the problem of curricular design, generating a method which we could then share with other data ethics educators. Since data ethics is a multidisciplinary field, it can benefit greatly from interdisciplinary collaboration. Furthermore, since our methodology can be applied widely to the survey of any discipline, we open source our work, in the hopes that it can be used to map other disciplines. Fundamentally, we are providing a methodology for curricular introspection.

The products of our research, are several. First, we provide a data set which describes a scholarly and pedagogical network. Next, we present a proof-of-concept interactive tool for exploring that data. We then present [an example syllabus informed by our findings](http://data-ethics.jonreeve.com/). Finally, we provide a template for a semantic, machine-readable course syllabus website, so that others can easily produce a syllabus using the same methods. All of this is available via our project's website, <https://data-ethics.tech>. This work is a collaboration between Columbia University researchers Jonathan Reeve (a PhD Candidate and Lecturer in computational literary analysis), Isabelle Zaugg, PhD (a Postdoctoral Research Scientist and Lecturer in critical data studies), and Tian Zheng (Chair of the Department of Statistics), with technical support from research assistants Serena Yuan and Zhuohan Zhang (MA students in Statistics). 

Our initial motivations were to collect data on the state of data science ethics, in order to answer broad questions, such as: 

 - Which texts are most frequently assigned, and cited? And which texts are excluded? Are there important outliers that deserve more attention?
 - Where are the disciplinary divides, and how can they be bridged?
 - What are similarities and differences between data ethics courses?
 - Which institutions, scholars, educators are innovating in this space? 
 - What are the major topic areas?

To explore these questions, and to give others the opportunity to explore them as well, we aggregated hundreds of syllabi, and hundreds of published papers, as well as adjacent and auxiliary data, from sources like CrossRef, Semantic Scholar, ORCID, and Wikidata. We then integrated this data into a large graph database, using the semantic web language known as the Resource Description Framework (RDF). 


# Background and Related Works

This project builds upon the work of a number of scholars who have sought to define and improve the field of data ethics education. Note that for the purposes of our analysis, we use the term “data ethics” as an umbrella term that encompasses the fields of AI ethics, tech ethics, data justice, and other overlapping subject areas aimed at improving technologists’ ethical foundations and delivering equitable impacts from data-driven practices. While this paper will not delve into the subtle overlaps and important distinctions between these unique fields of research and education, we acknowledge these distinctions and suggest the following literature for further insight [@fieslerWhatWeTeach2020; @haoStopTalkingAI2021; @metcalfPedagogicalApproachesData2015; @nkondeMutaleNkondeAI2021; @ochigameInventionEthicalAI2019; @rajiYouCanSit2021; @sloaneInequalityNameGame2019a; @taylorWhatDataJustice2017; @thomasConversationTechEthics2019; @zeffiroDataEthicsData2021]

In 2017, spurred by a New York Times article that argued that academics are “asleep at the wheel” when it comes to tech ethics [@oneilOpinionIvoryTower2017], Prof. Casey Fiesler crowdsourced a list of close to 200 tech ethics syllabi being taught primarily in the U.S [@fieslerTechEthicsCurricula2019]. This collection depicted the outline of a nascent field of education. This repository in its raw form was credited with helping many educators design or refine a syllabus, as well construct compelling arguments for the value of a tech ethics course at their institution [@fieslerTechEthicsCurricula2019]. It also sparked several analyses to understand the contours and blindspots of this emerging field.

Fiesler, along with co-authors Natalie Garrett and Nathan Beard, used metadata from 202 of these tech ethics courses to analyze “What Do We Teach When We Teach Tech Ethics” (2020). First, they explored the disciplinary spread of these classes in terms of a course’s home department, the instructor’s home department, and the instructor’s terminal degree. Computer Science was the most common departmental home both for courses and instructors, while Philosophy was the most common terminal degree. Next, they looked at major topic areas covered in these courses, the most common being Law & Policy, addressed in 57% of courses, and the least common being Medical/Health, addressed in less than 10% of courses. Finally, they assessed the most common learning outcomes promised students in these courses, including “critique,” “see multiple perspectives,” and “create solutions.”

Their analysis showed great variability across content taught, which they suggest is not surprising considering the lack of standards in the field and its transdisciplinary nature [@fieslerWhatWeTeach2020]. They suggest that this variability is positive; it represents an opportunity for educators to learn from one another's disciplinary expertise and teaching approaches. Despite variability, their analysis reveals key concepts considered critical in tech ethics, including algorithms, privacy, and inequality/justice. They also share a call to action to expand the field of tech ethics education. In particular, they highlight the need to develop approaches to fully integrate ethics into technical content for computer science (CS) students, especially at the impressionable initial stages of their education [@fieslerWhatWeTeach2020].

Our work builds upon Fiesler et al.’s work in several ways. First, our tool draws on the open-source syllabi shared in Fiesler’s repository [@fieslerTechEthicsCurriculum2017]. Second, our tool responds to the calls to action embedded within Fiesler et al’s analysis, namely to foster conversation among educators and bridge disciplinary divides. Third, our own resulting course design couples ethical reflection with computational practice and solution-building.

Our work also draws on the analysis of these syllabi by Inioluwa Deborah Raji, Morgan Klaus Scheuerman, and Razvan Amironesei’s in their 2021 FAccT conference paper, “You Can’t Sit With Us: Exclusionary Pedagogy in AI Ethics Education.” Their analysis surfaces patterns of what the authors call “exclusionary pedagogy” in AI ethics. The authors argue that the predominance of computer scientists as instructors of these courses, hierarchies of knowledge that elevate CS and other quantitative fields above the humanistic social sciences (HSS), and the siloing of the field from HSS perspectives, all promote techno-solutionism and the myth of technologists as “ethical unicorns” [@rajiYouCanSit2021]. They propose that tech ethics challenges are inherently interdisciplinary; therefore, education in this field must in turn include deep transdisciplinary collaboration and propose systemic rather than individualistic solutions.

Raji et al. argue that current gaps in transdisciplinary collaboration in AI Ethics can be perceived through the lack of transdisciplinary research output and siloed citations. This translates into the classroom vis-a-vis the assigning of literature with siloed citations. It is also reflected in the fact that only 2% of the 254 syllabi in their analysis allowed for “cross-disciplinary teaching or open courses with non-prohibitive requirements,” both of which would encourage and enable students from different disciplines to enroll in a data ethics course [@rajiYouCanSit2021].

In terms of our aspirations in the field of data ethics, this is important on two fronts. First, courses that bridge disciplines and do not require pre-existing technical proficiency have the potential to attract new cohorts of students to engage with computational fields [@zauggCollaboratoryColumbiaAspen2021]. It is important to bring students with ethical insights from other disciplinary backgrounds into the field of computation, and transdisciplinary data ethics coursework facilitate that. Second, by using data ethics as a bridge to open a new pathway into computational fields, there may be a potential to attract students from under-represented backgrounds who might otherwise hesitate to take foundational computational coursework because they don’t see themselves represented in the field.

Both potential “pipeline” outcomes have the promise to address the calls data ethicists have made regarding the need to diversify the computational workforce in terms of disciplinary expertise, demographics, and lived experience [@lueDataScienceFoundation2019; @themoore-sloandatascienceenvironments:newyorkuniversityucberkeleyandtheuniversityofwashingtonCreatingInstitutionalChange2018; @rawlings-gossKeepingDataScience2018; @westDiscriminatingSystemsGender2019]. While we can only speculate about the profiles of individual students taking these courses as well as the long-term outcomes of their learning, we hope this project will provide one small stepping stone towards further analysis and imagination of how data ethics education is (or could be) embedded within the disciplinary structures of universities, and the degree to which courses provide entrée into computational practice for students rooted in other disciplines.

Importantly, Raji et al. (2021) also highlight the need for courses to include student engagement with stakeholders from outside academia who are typically the most impacted by algorithmic harms. While this type of curricular approach largely escapes our tool’s scope, which is limited by its primary focus on assigned literature, this key aspiration in data ethics education is essential to highlight in the context of this paper.

Responding to these varied calls to action in the field of data ethics education, we aim for our text-to-text tool, which maps citation patterns, to visually highlight the issue of siloed citations and inspire cross-disciplinary collaboration. We also hope our tool’s accessible interface will spur exploration of material across disciplinary divides. In our own case, our syllabus design builds off of our varied expertise in the humanistic social sciences, statistics, and data science, and will be co-taught without computational prerequisites to encourage a disciplinarily-diverse cohort of students.

We also note the 2015 “Pedagogical Approaches to Data Ethics” report by Jacob Metcalf, Kate Crawford, and Emily Keller at the Data & Society Research Institute. Based on their survey of existing data ethics courses, and informed by research on best practices in science and engineering ethics education, they propose that the following four approaches to data ethics education should be encouraged:

>1) Integrative approaches are preferable to stand-alone modules...
>2) When possible, integration with design/practical work should be encouraged. Ethics should be associated with problem-solving, not just rule-following or prevention of harm.
>3) The micro-ethics of research should be intellectually and practically associated with broader social goods. Neither the RCR [Responsible Conduct of Research] approach nor broad social goods alone are adequate.
>4) Culture, collective responsibility, and collaboration are critical components of successful research ethics education. [@metcalfPedagogicalApproachesData2015, p. 3]

We developed our tool with the intention of facilitating further analysis, imagination, and innovation to strengthen the field of data ethics education. Providing our database and tool as a starting point, we suggest further research questions that draw on the insights and aspirations for the field shared by the scholars above. Research questions ripe for investigation include:

 - What patterns in data ethics education can we deduce from looking at similarities and differences between courses offered at different universities?
 - What are major topic areas in data ethics courses? Do they map onto particular approaches to promote ethical data science such as FAccT?
 - How many data ethics courses help students make the leap from “critique” to computational problem-solving?
 - How many courses are fostering cross-disciplinary collaboration?
 - How many courses include community stakeholder engagement?
 - How many courses are linking micro-ethics with an exploration of data scientists’ collective responsibility for the broader social good
 - How might our "roadmap" be useful for educators designing data ethics courses? What are its limitations (reducing a course to its assigned texts, for example) and how might they be addressed through complementary efforts?

# Methods

We begin with syllabi crowdsourced from Fiesler et al.’s study, which collects roughly three hundred syllabi in tech ethics [@fiesler_tech_2019]. We then augmented this with syllabi gathered from the Open Syllabus Project [@nowogrodzki2016mining], the AI Ethics Workshop [@ai_ethics], and elsewhere. These syllabi we then downloaded, mined for their assigned texts, using a partially automated method, and added to our graph database. 

Since the RDF technology we use prefers universal reference identifiers (URIs), we attempt to resolve our data to stable identifiers, wherever possible, using new data from a number of public databases. We resolve scholarly papers to digital object identifiers (DOIs), using metadata APIs such as those of [CrossRef](https://www.crossref.org/) and [Semantic Scholar](https://www.semanticscholar.org/), which we also use to enhance our available bibliographic metadata. We resolve books to stable identifiers by querying the [Google Books](https://books.google.com/) and [Open Library](https://openlibrary.org/) APIs. We resolve researchers and writers to their [ORCIDs](https://orcid.org/), where possible. Finally, we resolve university names to their websites and Wikidata entries.

Each of these additional data sources provides a number of advantages, beyond simply the resolution or deduplication of their entities in our database. Semantic Scholar, for instance, maintains data about the citation and reference network of a given paper. Open Library maintains information about the number of editions a given book has seen, worldwide. ORCID allows us to find the other publications by a given researcher, as well as demographic information about them. Wikidata provides us with geographic information about universities, which we may later use to plot these courses on a world map.

We then represent the resulting data, and its relations, as a series of subject-verb-object triples, in the Turtle syntax of the RDF. This graphical data structure is the next-generation language for representing structured data on the web. It is highly machine-readable and has ambitions to become "Web 3.0," a web of structured knowledge.

An example might look like this, as portrayed here in pseudo-RDF: 

```
<Course A> <is offered by> <Department A>
           <has a syllabus at> <https://example.edu/syllabus-location>
           <is taught by> <Instructor M>
           <is required by> <Department A>
           <has learning material> <Text A>

<Text A> <was written by> <Scholar A>
         <cites> <Text B> 
         <is cited by> <Text C> 

<Instructor A> <wrote> <Text B>
               <wrote> <Text C>
               <taught> <Course B>
               <has ORCID> <Orcid ID A>

<Department A> <is a department of> <University A>
               <has website> <http://department.example.edu>

<University A> <has latitude> <34.000>
               <has longitude> <37.000>
               <was founded> <1899>
        ...
```


[@Fig:chart] shows an example directed graph visualization of this structure, illustrating relations between these entities.

![Flow chart of ontology data](chart.png){#fig:chart}

In practice, however, each of these tokens must have a stable URI—even the verbs. Thus, we employ a number of pe-existing ontologies, or pre-defined sets of relations, to describe these relationships in a structured way. The Curriculum Course Syllabus Ontology (CCSO) describes relations between courses, universities, syllabi, professors, and learning materials such as texts [@katis_2018]; the Bibliographic Ontology (Bibliontology) describes metadata for articles, books, videos, and other media [@pertsas_2017]; and the Citation Typing Ontology (CiTO) describes citation relations between texts [@peroni2012]. We integrate these three, along with a few standard ontologies for defining people and things, such as the Friend-of-a-Friend (FOAF) ontology, and those used by Wikidata. For those entities which aren't resolvable to standard URIs, we provide one. This is the case, for example, for courses, which have URIs like <https://data-ethics.tech/course/1>. 

To make sense of these connections, we build a number of force-directed network visualizations in JavaScript, so that they may be explored by a wider public. This website has three main visualizations: university-course, course-text, and text-text. University-course represents universities and their courses as nodes, with edges that show which universities offer which courses. Course-text represents courses and the texts that they assign. And text-text represents those texts, and their citation/reference network. For each of these, we compute basic network statistics such as page rank, which allow users to see at a glance which texts are the most assigned, and which universities are best represented in our dataset. 

We also build a mechanism for users to submit their own data ethics syllabi to our database; this way, our database will always stay up to date. A further step will be to generalize this framework so that it may be used to map any academic discipline, given a list of courses and their syllabus URLs.

The process of parsing syllabi—traditional documents, usually in PDF or DOCX—into structured, machine-readable data, is a difficult, complex process. This led us to imagine a modern course syllabus, which would not only be web-ready, but 

be possible to write modern, semantic syllabi which were already ready to be understood by computers and humans alike. 

Finally, we provide a template for instructors to create a course website which already organizes course data in this structured, machine-readable way. In this manner, instructors can easily create a course website, while contributing to disciplinary metacognition.

# Findings and Contributions

Our methods contribute to data ethics education by providing a means for curricular introspection. For educators designing or refining a course, our tool provides an overview of the courses that are already being taught. The tool then provides an opportunity for educators to more easily imagine expansions of their syllabi beyond their expertise, and to pursue top aspirations in the field, such as teaching data ethics in a transdisciplinary manner, embedding computational problem-solving into coursework, and highlighting the perspectives of scholars from diverse backgrounds.

While patterns in data ethics education emerge organically from the data, we also intervene manually to identify and label some of these patterns. Patterns of possible interest to educators include clusters of courses at institutions, the most-assigned literature in the field, and thought-provoking outliers. In the future we plan for our tool to foreground patterns in citations as well as clustered topic modeling of core subject areas in the data ethics literature.

![Course-text graph](course-text.png){#fig:graph}

Our data visualization allows one to quickly identify both valuable patterns in texts assigned, as well as outliers. [@Fig:graph] shows a portion of our course-text graph, showing the most-assigned text our analysis identified: Friedman and Nissenbaum's 1996 paper "Bias in Computer Systems" [@nissenbaum1996]. When viewed as a text-text network, however, the rankings are very different: McLuhan's 1964 _Understanding Media_ is the most-cited node in our network [@mcluhan1994understanding]. We must treat these findings with skepticism, however, since they represent a dataset that is still very incomplete, and a node resolution process that is still under development. It makes sense that McLuhan's book is so widely cited, for instance, since its total count is an accumulation of its nearly 60 years of publication. 

In this sense, our contribution is not merely a list of answers to the questions we posed above. Rather than generating merely rankings of texts, and statistics about courses, we are more interested in creating a proof-of-concept system for exploration of a field, one which can be built upon by future researchers.

Our network visualizations models user engagement with both consensus and outliers, which is important considering that racial justice scholarship, feminist theory, and efforts to “decolonize curricula” have highlighted how the process by which texts gain importance and “enter the canon” is not always meritocratic and often “outsider” voices deserve to be centered. This is all the more true in a field such as data ethics where critical voices are challenging established perspectives, practices, and institutions. 

We then must conclude with calls for further research: either contributions to our project directly ([all of our code and data is open-source and available on GitHub](https://github.com/JonathanReeve/data-ethics-literature-review)), or projects which can employ our data or methods to new ends. We believe that these methods can be easily adapted and used to map many other fields of academic study. 

# Conclusion

As a multidisciplinary and quickly growing field, data ethics educators can benefit from a birds-eye view of curricular practice and real-time innovation. Our database and tool provide a starting point for this exploration and analysis. Our literature review provides an overview of the foundational aspirations of the field, which educators may wish to manifest within their course design. Top aspirations of the field include embedding ethics within computational problem-solving, offering multi-disciplinary courses without technical prerequisites as an entry point into the field for disciplinary and demographically diverse students, and embedding opportunities for students to engage with stakeholders of data-driven practices outside the halls of academia and the field of tech.

Our own course, "[People vs. Algorithms: Data Ethics in the 21st Century,](http://data-ethics.jonreeve.com/)" is informed by everything we learned from this project. While a minority of data ethics courses include practical components and work on solutions/pathways for mitigating these issues, our course includes practical exercises in putting those ideas to use. Teaching cross-disciplinarily between Stats, CS, humanities, social sciences, we have opened our course to a mixed classroom with no technical prerequisites. We are engaging with literature across many fields, teaching foundational computational skills and problem-solving alongside reading and writing assignments that engage with some of the most-cited thought pieces as well as important outliers. We push students beyond identifying ethical issues to identify new horizons of possible solutions. As we pilot and reiterate our course, we look forward to utilizing this tool to consider new perspectives and approaches in the field of data ethics education.

Most importantly, we hope that other educators benefit from the tool. As data ethicists ourselves, we care about openness and transparency, and so we have open-sourced this data, so that other researchers can use our work to answer their own questions. We hope that our framework may also be used to help map the institutional knowledge structures of even more disciplines.

# References

<!-- This section will be auto-generated. No need to put anything here manually. -->
