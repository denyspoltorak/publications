_[Part](../README.md)_ 1 2 **3** 4 5

---

# Introduction to Software Architecture with Actors: Part 3 – On Simple Systems

After having looked into the ways events are processed inside individual actors, it is time to try combining several actors (or splitting an actor by messaging interfaces).

- [The Coordinate System](#the-coordinate-system)
- [Shards / Instances](#shards--instances)
  - [Create on Demand (elastic instances)](#create-on-demand-elastic-instances)
  - [Leader/Followers (self-managing instances)](#leader-followers-posa2-self-managing-instances)
  - [Load Balancer, aka Dispatcher (external dispatch)](#load-balancer-aka-dispatcher-posa1)
  - [Mixtures](#mixtures)
- [Layers](#layers-posa1)
  - [Multi-tier System](#multi-tier-system)
  - [Thread Pool](#thread-pool)
  - [Application Pool](#application-pool)
- [Services](#services)
  - [Microservices (Domain Actors)](#microservices-domain-actors)
  - [Pipeline (Pipes and Filters)](#pipeline-pipes-and-filters-posa1)
  - [Nanoservices (Event-Driven Architecture)](#nanoservices-event-driven-architecture-sap)
- [ASS Compared to Scale Cube](#ass-compared-to-scale-cube)
- [Summary](#summary)
- [References](#references)

## The Coordinate System


![alt_text](images/image1.png "image_tooltip")


The remaining parts of the publication examine the relation between structural diagrams (drawings of components and their interactions) for common types of systems of actors/services and the properties of those systems. The following coordinates, abbreviated as **_ASS_,** will be used consistently:
* The vertical axis maps **_abstraction_** – upper parts are more abstract (high-level business logic in Python or DSL), whereas lower parts are implementation-specific (device drivers in C or highly optimized library data structures). Users pay for the higher levels of the software and don’t care about the low-level implementation unless something there goes wrong. The upper modules rely on the lower ones.
* The horizontal axis resolves **_subdomains_** in an arbitrary order. Moreover, the subdomains along the axis may vary (belong to different domains) at different heights (abstraction levels); for example, at the lower (OS) level, there is network, HDD, video, sound, mouse and keyboard drivers/interfaces, while the upper application level may be concerned with players, monsters and spells, and on top of it resides yet another layer with metadata: game scores, achievements, player rooms, etc. These different dimensions of subdomains should have been shown along dedicated orthogonal axes, but the drawing has only two available dimensions, making it necessary to map all the subdomains to a single axis of the diagram. Nevertheless, this does not make the diagrams overly messy, as the different domains are usually found at diverse heights (abstraction levels mapped to layers of the system).
* The Z-axis (which is hard to show in 2D and is thus directed diagonally) corresponds to **_sharding_** and shows multiple instances of modules. It is important for a few of the structures discussed and is omitted in other cases. 

I believe such coordinates are [common](https://en.wikipedia.org/wiki/Glibc#/media/File:Linux_API.svg) in [OS](https://en.wikipedia.org/wiki/Rump_kernel#/media/File:OS_rumparch.png) and embedded systems diagrams, but I have never seen the axes being explicitly named.

Sample diagrams of various basic shapes in an _ASS_ coordinate system will be analyzed by deducing the system properties from the structural diagrams and matched to well-known architectural patterns, with some coverage of common variants.

In some cases, it will be convenient to weaken the actors model by also covering synchronous interactions (RPC or direct method calls) between loosely coupled modules so as to include more examples.

## Shards / Instances


![alt_text](images/image2.png "image_tooltip")


**_Multiple instances_**. A monolith is cut into functionally identical pieces that usually don’t interact. Alternatively, several identical instances (_shards_) of a monolith are combined into a system to serve user requests together.

> _Why is inter-instance communication avoided? Because of possible race conditions (shown in the figure in red): if there were a task in shard[0] that needed shard[1] to change its data and another task in shard[1] that needed shard[0] to make changes, the system would struggle to stay consistent, in accordance with the CAP theorem [[DDIA](#DDIA)]. This is similar to deadlocks in synchronous systems; the preconditions for both handicaps are loops in control- or data-flow, caused by flows of opposing directions. As the creation of stable and evolvable systems involves avoiding handicaps, direct instance communication should be avoided._

> _If everything flows in the same direction (Pipeline [[POSA1](#POSA1)], discussed below), there are no opportunities for concurrent updates that could bring in inconsistency. If all the related data is kept together (Layers [[POSA1](#POSA1)], the next section), loops are also avoided, and the system state is consistent._

> _The best case is always the one that does not need processing. The green scenario in the figure above is very close to that: the shard gets a request, does some internal magic, and returns the response without having to deal with any outside modules, other shards included. This is possible if the shard owns all the information required for processing the events it gets assigned._

_Benefits_ (on top of those for _Monolith_ from Part 2):
* Sharding allows for nearly unlimited (being wary of the size of the dataset and traffic bottlenecks) scalability under load (by spawning more instances).
* Running multiple instances of an (ordinarily stateless) actor allows for synchronous calls (_Reactor_ [[POSA2](#POSA2)] from Part 2), simplifying the implementation of the business logic. The fact that the actors block for the duration of running tasks is compensated for by the number of actor instances.
* Fault tolerance – even if one instance crashes, the system still survives, and the unserved request may be forwarded to other instances, _except_ when the crash is reproducible – in that case, the request will crash all the actors it is forwarded to.
* Support for _[Canary Release](https://martinfowler.com/bliki/CanaryRelease.html)_ – it is possible to deploy a few instances of a new version of an actor for testing in parallel to the main workforce of a previous stable version.

_Drawbacks_ (on top of those for _Monolith_ from Part 2):
* Sharing data between shards is slower and gives rise to problems. Usually, the shards don’t know about each other, but see _Leader/Followers_ below and _Mesh_ in Part 5 for cases that rely on inter-shard communication. This drawback does not affect _stateless_ actors.
* There must be an entity that dispatches requests to shards; thus, this entity is a single point of failure.
* Deploying and managing multiple instances requires an extra administrative effort.

_Evolution_:
* If there appear new use cases that require a shard to access data that belong to other shards, a _shared repository_ (Part 4) is the most obvious solution. The structural changes needed may involve unsharding the entire application back to _Monolith_ (Part 2), splitting the database into a shared layer (the proper _Shared Repository_ pattern from Part 4), or running the shards on top of a _Space-Based Architecture_ framework (Part 5). Yet another option is _Nanoservices_ (see below).
* If in need of fine-grained scalability, splitting into _Nanoservices_ may be the best option for projects with small codebases, while for larger projects _(Micro-)Services_ (see below) or _Service-Oriented Architecture_ (described in Part 5) are more suitable.
* Fault tolerance may be achieved by [replacing parts of the monolith](https://hillside.net/plop/2020/papers/yoder.pdf) with _Nanoservices_ under _Microkernel_ (Part 4).
* Getting out of _monolithic hell_ [[MP](#MP)] can likely be achieved through sharded _(Micro-)Services_, in a way similar to that for unsharded monoliths.

_Summary_: sharding is a mostly free opportunity to scale a monolith to support higher load for isolated users or datasets of moderate size (before the database management or traffic control becomes non-trivial), though for larger systems, _Mesh_ (from Part 5) may be more appropriate. However, sharding is applicable only in cases where incoming requests may be binned to independent groups (i.e., no requests from one group touch the state that any other group writes to). \
_Example_: a network file storage where every user gets their own folder. A given folder’s URL maps to a single shard responsible for serving the user.

The code for shards is as simple to start writing as that for a monolith, and it faces similar threats, namely _monolithic hell_ [[MP](#MP)], as the project grows.

_Common names_: **Instances**.

_Software architecture_: **Pooling** [[POSA3](#POSA3)].

_System architecture_: **Sharding**, CGI/fCGI, FaaS.

Sharding is applicable to both monolithic applications and individual services or actors in more complex asynchronous systems. The latter case helps to remove bottlenecks in the system by creating more instances of the most heavily loaded modules than of modules under lower load, which results in an optimal use of resources.

Actor (or service) instances in a sharded architecture resemble execution threads in a multithreaded reactor. The difference between threads and processes is the source of most of the _Shards’_ benefits and drawbacks compared to those of a multithreaded _Reactor_ (Part 2).

I remember the next three approaches to dispatching the work among threads/instances:

### Create on Demand (elastic instances)


![alt_text](images/image3.png "image_tooltip")


The load (e.g. the number of simultaneous users for instance-per-user model) is unpredictable, or service instances may run on the client side. Create an instance as soon as a new client connects and delete it upon disconnect. This may be quite slow because of the instance creation overhead, and peak load may consume all the system resources, so new users will not be served. \
_Examples_: frontend, call objects in a telephony server, user proxies in multiplayer games and coroutines in _Half-Sync/Half-Async_ from Part 2. A stateless multithreaded _Reactor_ (Part 2) also fits the definition of _Shards_, as threads cannot change each other’s state – this is yet another case of a system that matches the descriptions of several patterns.

### Leader/Followers [[POSA2](#POSA2)] (self-managing instances)


![alt_text](images/image4.png "image_tooltip")


The instances are pre-initialized (_pooling_) and linked into a list. One instance (the _leader_) is waiting on a socket, while other instances (_followers_) are idle. As soon as the leader receives a request, it yields the socket to its first follower and starts processing the popped message. The follower that receives the socket becomes the new leader and starts waiting on the socket for an incoming request. As soon as one of the old leaders that were processing messages finishes its work, it joins the end of the followers queue.

This makes some sense but does not scale between servers. Thus, a hardware failure will kill the entire system.

### Load Balancer, aka Dispatcher [[POSA1](#POSA1)] (external dispatch)


![alt_text](images/image5.png "image_tooltip")


Some external service (Nginx or a hardware device) dispatches queries over an instance pool. This approach is scalable over multiple servers, but the balancer is the single point of failure.

Actually, this is a _layered_ system (see below), as the dispatcher and the shards belong to different abstraction levels; the dispatcher is concerned with connectivity (low abstraction: bytes, protocols, hardware) while the shards perform the business logic (high abstraction: users, goods, ads).

### Mixtures

Again, a couple of mixed cases are possible, e.g. when:
1. A _Load Balancer_ dispatches requests among servers that run _Leader/Followers_ queues.
2. All the instances on a server are waiting on an OS or framework object (e.g. a socket). An incoming request is assigned to one of the waiting instances. In this case, the _Load Balancer_ is implemented by the OS or the framework.

## Layers [[POSA1](#POSA1)]


![alt_text](images/image6.png "image_tooltip")


**_Separate the business logic from the implementation details._** The monolith is cut by messaging interfaces into pieces that model different abstraction levels. The uppermost level makes strategic decisions, whereas the lowest layer deals with the hardware.

_Benefits_:
* All the subdomains in any given layer are cohesive (accessible via synchronous calls). For example, in a game, the code for a unit may easily get information about its environment and interact with other units. This also makes debugging markedly easier unless the control-/data-flow under investigation leaves the current layer.
* The high-level logic is decoupled from the low-level code, e.g. a unit’s AI planner does not care about the unit’s rendering, as it is encapsulated with a messaging interface. This should (in theory) provide for more compact and readable code.
* The high-level logic and the low-level code may have different properties (_quality attributes_ or _“-ilities”_ [[MP](#MP)]) to satisfy conflicting _non-functional requirements_. A unit’s AI may be busy planning (which is a single long calculation) its future actions for a couple of seconds, while a renderer should draw (a periodic real-time task) the unit every 15 ms.
* All the layers may be executed in parallel (a layer per CPU core). However, the load distribution is usually quite unbalanced, making whatever benefit that is gained insubstantial.
* Layers that don’t possess a system-wide state may be independently sharded under load. For example, it is hard to shard a map (which is a unique shared resource), but it is practicable to shard the units’ AI planners (as they don’t interact directly).
* The layers may be deployed independently (take OS updates as an example), though not without some [effort](https://kb.netgear.com/21853/What-is-the-dual-image-feature-and-how-does-it-work-with-my-managed-switch) in terms of architecture and implementation.
* Layers support fast and easy processing of events that don’t involve multiple layers (e.g. the renderer may render the last cached state of the world without any need for direct access to the full units or map data).

_Drawbacks_:
* It is quite inconvenient to code and debug use cases with logic that is spread over multiple layers. In practice, the entire business logic often resides in the topmost layer or is divided between a UI/metadata layer that governs the system’s behavior and the domain model layer that implements most of the interactions (see _Application Service_, _Plug-ins_, _DSL_ and _Orchestrators_ in Part 4 of this series).
* Responsiveness and efficiency deteriorate if an incoming event has to traverse several layers to be handled. In practice, lower layers tend to combine several low-level system events into larger and more meaningful app-level events, decreasing the communication overhead towards the business logic layer(s).
* As the project evolves, one of the layers (usually the uppermost one) tends to grow out of control. The application of the _Layers_ pattern does not efficiently reduce the project’s complexity, though it may help with implementing the business logic in relatively high-level terms.

_Evolution_:
* The most common issue with layered structures is _monolithic hell_, when one of the layers grows too large for the developers to understand. Getting out of it requires splitting the overgrown layer(s) into services. The resulting system will usually consist of _(Micro-)Services_ (see below), often featuring _Application Service_ or _Shared Database_ (both described in Part 4). Other options include _Pipeline_ (described below), which is applicable to data processing systems, _Service-Oriented Architecture_ and _Hexagonal Hierarchy_ (both from Part 5). 
* Often, the business logic must be protected from external dependencies. This is achievable with _Hexagonal Architecture_ (Part 4) or _Pipeline_.
* Customization and metadata are available by applying _Plug-Ins_ or _Domain-Specific Language_ (both from Part 4).
* Satisfying contradictory non-functional requirements requires splitting the business logic into multiple services. _Shared Repository_ (Part 4) is likely to be the first step of the process.
* Scalability and fault tolerance will likely require sharding, with a subsequent transition to _Service-Oriented Architecture_ (Part 5) or _Nanoservices_ being possible if needed.

_Summary_: a cheap division of labor for cases with cohesive code at each abstraction level, while the levels themselves are loosely coupled (like game logic and renderer). _Layers_ are ubiquitous as a convenient approach which is hard to misuse.

_Common names_: **Layers** [[POSA1](#POSA1)].

_System architecture_: **n-Tier**.

Splitting into layers, like sharding, can be applied to monoliths, to individual actors or services, and even to whole systems containing multiple asynchronous components (e.g. _SOA_, _Mesh_ and _hierarchical_ architectures from Part 5). In other cases, prominent throughout Part 4, a monolithic layer is added to an existing system, usually to improve communication between its components. On rare occasions, subdomains may vary in the number of layers employed, the most common example of such a case being [CQRS](https://herbertograca.com/2017/10/19/from-cqs-to-cqrs/), where the command path uses a domain model layer (often with DAO) that is totally absent from the query path (which may sometimes consist of a barebone SQL editor).

As it usually happens, there are variants or corner cases:


![alt_text](images/image7.png "image_tooltip")


### Multi-tier System

A system is usually divided into layers/tiers according to the level of abstraction. With _3-tier_ web services, users face the highest abstraction _frontend_ layer, where domain concepts are represented with text, input fields, buttons and animations without heavy mathematical calculations. The next layer, _backend_, contains inheritance trees, if…elseif...else decisions, algorithms and containers embedded in _domain objects_ [[DDD](#DDD)] and _use cases_. Below that is a _data layer_ that contains tables and indices optimized for efficiency at the cost of resemblance to the domain entities. Every layer is very likely to be implemented in a dedicated programming language which better fits the layer’s needs (or which the available programmers are familiar with). The separation of implementations, including the choices of languages, is achieved via language-independent interfaces (e.g. HTTP and SQL for most of 3-tier systems, libc API and syscalls for Linux OS).

Externally-defined interfaces allow for layered architectures to apply equally well to objects, actors and mixed systems; a frontend may communicate with a backend asynchronously (in an actor-like way), while the backend makes synchronous RPCs to the data layer.

A typical 3-tier system may use several sharding options at once: the instances of the frontend layer are dynamically created on end-user devices, while the backend relies on a load balancer and an instance pool, albeit with the data layer left unsharded (a single-box DB instance).

The backend load balancer has been excluded from the figure, as it is a minor part of the system (it does not implement any business logic) and there was no convenient place for it in the drawing. However, it could have been shown between the frontend and the backend instances intercepting their communication channels, or at the very bottom as an entity with no business logic. Some details will be skipped from now on, as _too much information is no information._

Layered actors may be used in embedded programming to split the behavior of a control system into a long-term strategy and real-time reflexes, which are commonly programmed into separate chips. In telecom client devices, there are MMI (user interaction and high-level use cases), SDK (low-level use case support and common services) and FW (hardware-specific code) components.

### Thread Pool

A common pattern for offloading long calculations from a main business logic module to service threads that:
* May load all the available CPU cores with the calculations.
* May run in lower priority to avoid starving the main business logic thread(s).
* Run the assigned task to completion, then notify the task creator asynchronously.
* Accept any tasks, as the service threads don’t have any state or business logic of their own.

_Thread Pool_ looks like _Layers_ + _Sharding_. The management layer that runs the business logic creates and dispatches tasks while the service threads act as mere wrappers for the hardware’s CPU cores.

### Application Pool

This structure is a mirror reflection of _Thread Pool_. Instead of dumb threads ready to help with any tasks, _Application Pool_ manages instances that contain the entire application’s business logic, each serving user requests.

The _coroutines_ of _Half-Sync/Half-Async_ (from Part 2) may be considered application instances over a shared service layer; even the “Half-/Half-” in the pattern’s name evokes the notion of layers. In fact, the pattern itself originally described the kernel and user space layers of OSes. 

A backend with a _load balancer,_ described in the _Shards_ section above, is also an example of the _Application Pool_ architecture; there is a minor low-level component nearly devoid of business logic that governs high-level application components (CGI).

Yet another example may probably be found in _orchestrator_ [[MP](#MP)] (see Part 4) frameworks.

## Services


![alt_text](images/image8.png "image_tooltip")


**_Divide by functionality_**. An initial monolith is cut into actors that cover individual subdomains, with the expectation that most use cases don’t cross subdomain borders.

_Benefits_: \
* Decoupling subdomains is the only scalable way to reduce the code complexity, as the division results in pieces of more or less equal sizes. 
* Coding and debugging for an individual subdomain is easy, even when the high-level logic is strongly coupled to low-level details.
* The subdomains’ logic is kept loosely coupled for the duration of the project (i.e. modularity is not violated), as it is extremely hard to hack around a messaging interface even under pressure from management.
* The subdomains are decoupled by properties: one actor may be implementing real-time cases, while for another one, long-running tasks are common.
* All the subdomain implementations run in parallel.
* The subdomains can be sharded independently if the load varies and the subdomain does not have a global state.
* The subdomain actors may be deployed independently.
* Use cases that don’t cross subdomain borders (i.e., are limited to one subdomain) are very fast.

_Drawbacks_: \
* Use cases that involve logic or data from several subdomains are very hard to code and debug.
* If several services depend on a shared dataset, the data often needs to be replicated for each service, and the replicas (_views_ [[DDIA](#DDIA)]) should be kept synchronized.
* The system’s responsiveness and throughput deteriorate for system-wide use cases (that involve several subdomains).
* Services are left interdependent by contract (_choreography_ [[MP](#MP)]) unless there is a shared layer for coordinating inter-service communication and system-wide use cases (see Part 4 for multiple examples).
* Integration / operations / system administration complexity emerges.

_Evolution_: \
* Should individual services grow too large and complex, causing _monolithic hell_ [[MP](#MP)], they should be split into smaller services, likely transferring the system to _Cell-Based Architecture_ (Part 5). There are also the more dubious options of _Application Service_ (Part 4) and _Service-Oriented Architecture_ (Part 5).
* Having too many connections between services can be alleviated by introducing _Middleware_ (Part 4) or refactoring to _Cell-Based Architecture_ (Part 5).
* Protecting the business logic from the environment is achievable in the following ways: the whole system of services can be encapsulated with _Gateway_ (Part 4), while _Hexagonal Architecture_ (also from Part 4) can be applied to isolate the business logic of the individual services from third-party components.
* The project can often be developed faster when _Shared Repository_ or _Middleware_ (both from Part 4) is used.
* If the domain is found to be strongly coupled, the services either need to be integrated with a monolithic layer, i.e. _Application Service_ with _Orchestrators_ or _Shared Repository_ (all described in Part 4), or the entire business logic should be merged into _Hexagonal Architecture_ (Part 4) or even _Monolith_ (Part 2).
* The mutual dependency of services, caused by their reliance on each other’s interfaces and contracts, is reduced by the application of patterns that manage the communication and global use cases. _Middleware_ (Part 4) abstracts the transport, _Shared Repository_ (Part 4) provides communication via changes in the global state, while _Gateway_ (with _Mediators_ or _Orchestrators_) or _Application Service_ (all described in Part 4) takes control of global use cases, thus often removing the need for direct interservice communication. _Mesh_ and _Hierarchy_ patterns from Part 5 may completely remove the need for some of the communication aspects in project domains to which they are applicable.
* Extra flexibility and testability can be found with _Pipeline_ (see below), but it only fits simpler kinds of data processing.
* High scalability and fine-tuned fault tolerance are achievable with _Nanoservices_ (see below) and distributed _Microkernel_ (Part 4).

_Summary_: this kind of division is good for systems that feature mostly independent modules; otherwise, the implementation complexity and request processing time increases. \
_Exception_: for huge projects, the division by subdomain is the only way to keep the total project complexity manageable. Even though many use cases become intrinsically more complex to implement and operational complexity may become untrivial, the splitting of a huge monolith into several asynchronous modules still removes much of the accidental complexity in the code and allows the resulting modules to be developed and deployed relatively independently, leading one out of _monolithic hell_ [[MP](#MP)].

> _Other ways to split a huge monolith don’t reduce the code complexity well enough: sharding does not change the code at all (as every instance includes the entire project’s codebase), while layered systems usually contain 3 to 5 uneven layers, with one of the upper layers still growing too large to be manageable and too cohesive to be split again. At the same time, dividing a project by subdomain boundaries may easily result in a dozen loosely coupled services of nearly uniform size, and it may be possible to recursively split those services into subsubdomains if the need arises. The system as a whole becomes slower and more complicated, but the individual components remain manageable. There is another similar, yet better, option, namely hierarchical decomposition (described in Part 5), but it is not applicable in most domains._

_Common names_: **Actors** (embedded).

_System architecture_: **Microservices** [[MP](#MP)].

Like the other two basic patterns described in this article, splitting into services applies to both monoliths and individual modules. Three kinds of architectures that result from splitting a monolithic application into services are described in the subsequent sections. Part 4 is dedicated to architectures that retain a monolithic layer together with layers of services, whereas Part 5 deals with fragmented systems where every layer has been divided into subdomain services.

Traditionally, there are variants:

### Microservices (Domain Actors)

**_Make subdomains independent._** If a target domain can be divided into several subdomains, it is likely that the business logic inside each of the subdomains is more cohesive than it is between the subdomains, meaning that any given subdomain deals with its own state and functions much more often than it requires help from other subdomains. Tasks limited to a single subdomain are easy, those chaining (_fire and forget_) or multicasting notifications over several subdomains – acceptable, but once a task requires the coordination of and feedback from several subdomains – everything turns into a mess (see Part 1), as the subdomain actors are too independent. Not only do _views_ [[DDIA](#DDIA)] or _sagas_ [[MP](#MP)] emerge, but the task’s logic is likely to consist of multiple distributed pieces, possibly belonging to several code repositories, which makes troubleshooting the task as a whole very inconvenient, and its execution often inefficient. A system that mostly relies on such coordinated tasks is sometimes called a _distributed monolith_ [[MP](#MP)] (Part 5) and is usually considered to be the result of an architectural failure, namely incorrect subdomain boundaries or overly fine-grained services [[SAP](#SAP)]. It is recommended to [first build a monolith](https://martinfowler.com/bliki/MonolithFirst.html), then locate loosely coupled modules [[DDD](#DDD)] (possibly refactoring out redundant dependencies and moving pieces of code between modules), and only after the already running system has converged into a loosely coupled state can it be split into a set of microservices. Another option to reduce a monolith is by [separating the most loosely coupled services](https://hillside.net/plop/2020/papers/yoder.pdf) on an individual basis. This is a lengthy process, but it does not destabilize the whole project.

_Domain Actors_ / _Microservices_ may be used for loosely coupled _data processing_ (enterprise) and _control_ (telecom) systems; see Part 2 for the distinction. 


![alt_text](images/image9.png "image_tooltip")


When things go wrong (as they tend to do in real life), systems start to rely on distributed transactions, causing _sagas_ [[MP](#MP)] (rules for running system-wide transactions and rolling back failed ones) to be implemented. They may be _choreographed_ [[MP](#MP)] by hardwiring the task processing steps into services or _orchestrated_ [[MP](#MP)] by adding an extra business logic layer on top of the services. A choreographed logic is hard to understand, as a single use case is split over multiple code repositories, while an orchestrated logic adds a system-wide layer on top of the services; it is slower because more messaging is involved and may create a single point of failure.

For this and other practical reasons, real-world _microservice_ systems are usually augmented with extra layers such as _Gateway_ [[MP](#MP)], _Orchestrators_ [[MP](#MP)], _Shared Database_, or _Message_ _Broker_ [[MP](#MP)] – all of which are described in Part 4 of the series, or are _Hierarchical_, with _Hexagonal_ or _Cell_ subsystems for services (Part 5).

### Pipeline (Pipes and Filters [[POSA1](#POSA1)])


![alt_text](images/image10.png "image_tooltip")


**_Separate data processing steps_**. A special case of _Domain Actors_ (_Broker Topology_ [[SAP](#SAP)]), it is very specialized but widely used; while in most other patterns, participants may communicate in any direction, _Pipeline_ is limited to unidirectional data flow – every actor (called a _filter_ in this pattern) receives its input data from its input event pipe(s), processes the data and sends results to its output message pipe(s). A filter is usually responsible for a single step of the data processing and is kept small and simple.

The filters can be developed, debugged, deployed and improved independently of each other [[DDIA](#DDIA)] thanks to their identical interfaces (though input data type tends to vary) – in fact, the filters are completely ignorant of each other’s existence, a nearly unachievable goal for microservices. Event replay (with a data sample from a pipeline) is used for profiling and for the comparison of outputs between versions of a filter [[DDIA](#DDIA)]. Pipelines sometimes branch and in rare cases may change topology at run time. Pipelines are usually created by a factory during system initialization, often based on a configuration loaded from a file.

This pattern is only useful in _dataflow_-dominated systems (as _control_ systems both tend to change behavior at run time and usually need real-time responsiveness – see Part 2). Nevertheless, if _Pipeline_ fits the project’s domain requirements, it may be used without much further investigation, as the pattern is very flexible and simple. However, there are some domains dominated by data processing delay (instead of the more common throughput objective), namely night vision, augmented reality and robotics, where pipelines are inappropriate solely because the pattern is not optimal for fast response time. 

_Benefits_:
* It is exceedingly easy to develop and support.
* The filters run in parallel, allowing the OS to distribute the load over the available CPU cores.

_Drawbacks_: 
* If some of the filters are slower than others, there is a chance of the data overrunning the pipe’s capacity and starving the OS of RAM when under heavy load. This can be alleviated by implementing a feedback engine, which, however, complicates the simple idea of pipelines.
* _Pipes and Filters_ are likely to suffer from copying the data more often than strictly necessary, and the pattern is not well suited for the parallelization of data processing inside individual filters. This means that a decently written _Monolithic_ application (probably using a _Thread Pool_) will process each data packet faster, and is very likely to have better throughput.

_Evolution_:
* Fine-grained scalability and fault tolerance may require a transition to _Nanoservices_ in a _Microkernel_ environment (Part 4).

_Common names_: **Pipes and Filters** [[POSA1](#POSA1)].

_System architecture_: **Pipelines** [[DDIA](#DDIA)].

Implementing feedback (_[congestion control](https://en.wikipedia.org/wiki/TCP_congestion_control)_) for highly loaded pipelines may require the filters to send back a confirmation for every processed packet, the number of packets in a pipe, or the number of packets that have already been processed. This effectively creates a system where _data_ and _control_ (feedback) packets flow in opposite directions. Another feedback option is to add a supervisor _middleware_ (Part 4) that collects throughput statistics and manages the quality/bitrate settings of the filters to avoid overloading the pipeline A third feedback option is to make writing to a pipe block if the pipe is full [[POSA1](#POSA1)]. 

### Nanoservices (Event-Driven Architecture [[SAP](#SAP)])


![alt_text](images/image11.png "image_tooltip")


**_Fine-grained actors for supreme fault tolerance, flexibility and scalability_**. _Event-Driven Architecture_ is an umbrella term for approaches that use some of the following features:
* An actor (_event processor_) for each data processing step (stateless) or domain entity (stateful): the proper _Nanoservices_
* _Publish-Subscribe_ communication
* Pipelined (unidirectional) and often forked flow that tends to involve persistence (database access, event sourcing or a built-in framework capability)

Strictly speaking, _Microservices_ and _Pipelines_ are also _Event-Driven Architectures_, but the name is often used for _pipelined pub/sub nanoservice systems_.

Like in _Pipeline_, an external event passes through multiple steps that transform it, usually by adding more data. In contrast to _Pipeline_’s _filters_, _event processors_ may mark the event as disallowed to break the normal processing chain, and they tend to read from or write to **shared** databases. Unlike with _Pipelines_, multicasts, either via pub/sub subscriptions or by _Mediator_ [[SAP](#SAP)] (Part 4), are common.

_Choreography_ [[MP](#MP)] (_Broker Topology_ [[SAP](#SAP)]) and _orchestration_ [[MP](#MP)] (_Mediator Topology_ [[SAP](#SAP)]) apply, just like for _microservices_. Unlike _microservices_, _event processors_ are very fine-grained, usually containing code for a single action or domain entity, and are spawned in large numbers.

While most of the system architectures feature four levels to distribute the domain complexity over, namely: lines of code in methods, methods in classes, classes in services, and services in the system (see Part 1 for the relevant discussion), _nanoservices_ feature only the first and the last means, as a nanoservice implements a single method. Therefore, this pattern is not applicable for complex domains.

_Benefits_:
* Very good fault tolerance is achieved, as every part of the business logic and every user request is isolated.
* _Nanoservices_ run in parallel, allowing the OS to distribute the load over CPU cores or a load dispatcher to spread requests to multiple servers.
* _Nanoservices_ are nearly perfectly scalable unless they access a shared database (which they do) or saturate the network bandwidth / run out of money in cloud deployments.
* Individual _nanoservices_ are easy to develop and support.
* Individual _nanoservice_ implementations may be reused.
* The system is evolvable by inserting new _nanoservices_ or rewiring the existing ones unless it grows too complex to grasp all the interactions and contracts.

_Drawbacks_: 
* Integration complexity may quickly overwhelm the project.
* Debugging and testing will not be easy.
* Any coordinated database writes will either limit the system to a single shared database or require distributed transactions or _sagas_ [[MP](#MP)], increasing complexity and limiting scalability.
* Component reuse is not always going to work because contracts may vary.
* Too much communication wastes system resources, often increases response times and limits scalability.

_Evolution_:
* _Microkernel_ frameworks (from Part 4) allow for a fast start on the project and the handling of failure recovery in the application code.
* _Space-Based Architecture_ (from Part 5) may help to distribute the shared repository.

_Common names_: Actors (telecom), Flowchart.

_System architecture_: **Nanoservices**, Event-Driven Architecture [[SAP](#SAP)].

_Nanoservices_ provide good flexibility and scalability for simple systems with few use cases but tend to turn into an integration nightmare as the functionality grows. Moreover, the almost inevitable use of [shared databases](https://peterdaugaardrasmussen.com/2019/08/14/what-is-a-nano-service/) (as one nanoservice is dedicated to creating users, another to editing them, and the third and fourth to deleting and authorizing them, respectively) limits most of the benefits. The system diagram looks very similar to a _flowchart_; ultimately, that’s likely what stateless nanoservices are, except that flowcharts for all the implemented use cases coexist in the production system. This assumption is confirmed by the visual programming tools (like jBPM) being advocated [[SAP](#SAP)] for nanoservices.

Distributed actors frameworks, e.g. Akka or Erlang, are often used for stateful _Nanoservices_, providing a fault-tolerant _Microkernel_ environment (described in Part 4).

## ASS Compared to Scale Cube

[[MP](#MP)] defines _scale cube_ as a means of scaling an application in the following ways:
1. Cloning instances (which corresponds to sharding a backend in ASS)
2. Functional decomposition (splitting a monolith into microservices)
3. Data partitioning (which corresponds to sharding a data layer in ASS)

The ASS diagrams used throughout the current series of articles represent _evolvability_ (how easy it is to change the system) through decoupling:
1. Decoupling by **A**bstraction level
2. Decoupling by **S**ubdomain
3. **S**harding

Two dimensions of ASS (abstraction and subdomain) correspond to the functional decomposition of scale cube, while both the cloning and the data partitioning of scale cube match to ASS’s sharding at different abstraction levels.

[[DDIA](#DDIA)] mentions _scaling up_ (upgrading CPU, RAM and disk space) vs _scaling out_ (going distributed).

Any conclusions? It seems that the coordinate system used in this cycle is unrelated to the scaling coordinates, except for the fact that every diagram is limited to 2 or 3 dimensions. Nevertheless, some kind of sharding is present in all the coordinate systems reviewed.

## Summary

All the possible ways of splitting a monolith along one of the ASS dimensions were described, creating:
* _Shards_ from spawning monolithic instances. 
* _Layers_ from slicing by code abstractness.
* _Services_ when divided by subdomain.
* _Pipeline_ and _Nanoservices_ as common specializations of _Services_.

The next parts will cover divisions along both abstraction and subdomain dimensions.

## References

<a name="DDD"/>

[DDD] Domain-Driven Design: Tackling Complexity in the Heart of Software. _Eric Evans. Addison-Wesley (2003)._

<a name="DDIA"/>

[DDIA] Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems. _Martin Kleppmann. O’Reilly Media, Inc. (2017)._

<a name="EIP"/>

[EIP] Enterprise Integration Patterns. _Gregor Hohpe and Bobby Woolf. Addison-Wesley (2003)._

<a name="MP"/>

[MP] Microservices Patterns: With Examples in Java. _Chris Richardson. Manning Publications (2018)_.

<a name="POSA1"/>

[POSA1] Pattern-Oriented Software Architecture Volume 1: A System of Patterns. _Frank Buschmann, Regine Meunier, Hans Rohnert, Peter Sommerlad and Michael Stal. John Wiley & Sons, Inc. (1996)._

<a name="POSA2"/>

[POSA2] Pattern-Oriented Software Architecture Volume 2: Patterns for Concurrent and Networked Objects. _Douglas C. Schmidt, Michael Stal, Hans Rohnert, Frank Buschmann. John Wiley & Sons, Inc. (2000)._

<a name="POSA3"/>

[POSA3] Pattern-Oriented Software Architecture Volume 3: Patterns for Resource Management. _Michael Kircher, Prashant Jain. John Wiley & Sons, Inc. (2004)._

<a name="SAP"/>

[SAP] Software Architecture Patterns. _Mark Richards. O’Reilly Media, Inc. (2015)._

---

_Editor:_ [Josh Kaplan](mailto:joshkaplan66@gmail.com)

 
_[Part](../README.md)_ 1 2 **3** 4 5

---

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.