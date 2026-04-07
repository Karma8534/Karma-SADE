# BestPractices

*Converted from: BestPractices.PDF*



---
*Page 1*


Open in app
11
Search Write
Let’s Code Future
Member-only story
30 Most Important
System Design
Concepts in Just 30
Minutes
A beginner-friendly roadmap to mastering
system design from fundamentals to scalable
systems
Deep concept Following 32 min read · 17 hours ago
68


---
*Page 2*


👋
Hey devs
System Design can feel overwhelming at first.
Nonmembers click here
When you’re just starting out, everything looks
complex scalability, load balancing, caching,
distributed systems… and you don’t even know
where to begin.
I’ve been there.


---
*Page 3*


But here’s the truth: once you understand the core
building blocks, everything starts to click. What
once felt confusing begins to feel logical even
predictable.
In this story, I’m breaking down the 30 most
important System Design concepts every
developer should know whether you’re preparing
for interviews or trying to build real-world scalable
systems.
These aren’t just theoretical ideas.
Let’s get into it
The Foundation
1. Client–Server Architecture
Almost every app you use today whether it’s a
website, a mobile app, or even a game is built on a
simple but powerful idea: client–server
architecture.


---
*Page 4*


At a high level, there are two sides.
On one side, you have the client this is what you
interact with. It could be your browser, a mobile
app, or any frontend interface.
On the other side, you have the server a machine
that runs continuously in the background, ready to
handle requests from clients.
Here’s how they work together:


---
*Page 5*


The client sends a request (like fetching data,
saving something, or updating information)
The server receives that request
It processes the logic, interacts with the
database if needed
And then sends back a response
That’s it. Simple loop: request → process →
response
But this simplicity hides something interesting.
Because now a natural question comes up:
How does the client actually know where the server
is…?
That’s where things start getting more
interesting… and that leads us to the next concept.
2. IP Address
In the previous section, we left with a question:


---
*Page 6*


How does a client actually find the server?
To communicate with a server, the client needs an
address.
On the internet, this address is called an IP
address.
You can think of it like a phone number for a
server.


---
*Page 7*


Just like you need someone’s phone number to call
them, a client needs a server’s IP address to send a
request.
Every server on the internet has a unique IP
address.
So when a client wants to interact with a service, it
sends its request to that specific address.
Simple enough… but here’s the problem.
When you visit a website, you don’t type something
like:
142.250.183.206
You type:
google.com
Because let’s be honest
no one wants to remember a bunch of random
numbers for every website they use.


---
*Page 8*


And there’s another issue.
If a company moves its server to a different
machine, the IP address can change.
Which means every client trying to connect using
the old IP would simply fail.
So now we have a clear problem:
We need something that is easy for humans to use…
but still maps to the correct IP address.
And that’s exactly what the next concept solves.
3. DNS (Domain Name System)
In the previous section, we saw the problem:
IP addresses are hard to remember.
So instead of typing something like:
142.250.183.206
we use something much more human-friendly:


---
*Page 9*


domain names (like google.com)
But this creates a new question:
How does a domain name get converted into an IP
address?
That’s exactly where DNS (Domain Name System)
comes in.
Think of DNS like the contact list on your phone.


---
*Page 10*


You don’t remember everyone’s phone number
you just remember their name, and your phone
finds the number for you.
DNS works the same way.
It maps:
domain name → IP address
What happens behind the scenes?
When you type a domain (like google.com) into
your browser:
1. Your system sends a request to a DNS server
2. The DNS server looks up the IP address for that
domain
3. It returns the IP address back to your system
4. Your browser then uses that IP to connect to the
actual server
And just like that — the website loads.


---
*Page 11*


You can actually see this in action.
Open your terminal and run:
ping google.com
You’ll get the IP address currently mapped to that
domain.
Now everything connects together:
Client needs an address → IP Address
Humans can’t remember IPs → Domain Names
Domain → IP mapping → DNS


---
*Page 12*


And this is how the internet becomes usable for
humans.
But now another question comes up:
👉
What happens between the client and server once
the connection is established?
4. Proxy & Reverse Proxy
So far, we’ve seen how a client finds and connects
to a server.
But in real-world systems, something interesting
happens:
your request doesn’t always go directly to the
server.
Sometimes, it goes through a middle layer first.
What is a Proxy?
A proxy server acts as a middleman between you
(the client) and the internet.


---
*Page 13*


Instead of sending your request directly to a
website:
You → Proxy → Server
Server → Proxy → You
The proxy forwards your request, gets the
response, and sends it back to you.
Why use a Proxy?
The biggest benefit is privacy.


---
*Page 14*


Since the request goes through the proxy:
the server sees the proxy’s IP, not yours
your real identity and location stay hidden
This is commonly used in:
VPNs
corporate networks
restricted environments
What is a Reverse Proxy?
A reverse proxy sits on the server side instead of the
client side.


---
*Page 15*


Now the flow becomes:
Client → Reverse Proxy → Backend Servers
Here’s what it does:
receives incoming requests
decides which server should handle them
forwards the request internally
Why use a Reverse Proxy?
Because exposing servers directly to the internet is
risky.


---
*Page 16*


A reverse proxy:
hides actual server IPs
protects against attacks (like DDoS)
controls and filters incoming traffic
helps distribute load across multiple servers
Simple Way to Remember
Proxy → protects the client
Reverse Proxy → protects the server
Now your system is getting more realistic.
Instead of direct communication, we’re adding
layers of control, security, and scalability.
And this naturally leads to another important
question:
👉
How do we measure how fast or slow these requests
are?
5. Latency


---
*Page 17*


Now that we understand how clients connect to
servers, let’s talk about something you’ve definitely
felt before:
delay
Whenever a client communicates with a server,
there is always some delay.
Even if everything is working perfectly.
This delay is called latency.
Why does latency happen?


---
*Page 18*


One of the biggest reasons is physical distance.
Imagine this:
Your server is in New York
Your user is in India
When the user sends a request:
the data has to travel thousands of kilometers
reach the server
and then the response has to travel all the way
back
This full journey is called:
round-trip time
And that’s exactly what latency measures.
How do we reduce latency?
A common solution is:
deploy servers closer to users


---
*Page 19*


Instead of having one server in a single location,
companies use:
multiple data centers around the world
So now:
users connect to the nearest server
data travels a much shorter distance
latency becomes much lower
Simple way to think
Closer server = faster response
Now we’ve covered:
how clients find servers
how they connect
and how long communication takes
Which leads to the next question:


---
*Page 20*


Once connected, how do they actually communicate
with each other?
6. HTTP & HTTPS
Now that a client has found the server and
established a connection…
how do they actually talk to each other?
They follow a set of rules called HTTP (Hypertext
Transfer Protocol).


---
*Page 21*


That’s why most URLs start with:
http://
or its secure version https://
How HTTP works
Whenever you open a website:
Your browser (client) sends a request to the server
The request includes:
headers (metadata like browser type, request
type, cookies)
sometimes a body (data like form inputs)


---
*Page 22*


The server processes the request
It sends back a response:
either the requested data
or an error (like 404, 500, etc.)


---
*Page 23*


That’s the basic communication loop.
The problem with HTTP
HTTP sends data in plain text.
Which means:
anyone intercepting the request can read it
passwords, credit card details, personal data →
all exposed
Clearly… not ideal.
Enter HTTPS
To solve this, we use HTTPS (HTTP Secure).
HTTPS encrypts all communication using
SSL/TLS.
So now:
data is encrypted before sending
even if intercepted, it’s unreadable


---
*Page 24*


no one can tamper with it
This is why almost every modern website uses
HTTPS.
Important clarity (this part most beginners miss)
HTTP only defines how data is transferred.
It does not define:
what the data should look like
how requests should be structured logically
how different systems should interact
In simple terms:
HTTP = transport layer (how data moves)
NOT = what data means
So what defines the structure?
That’s where APIs (Application Programming
Interfaces) come in.
APIs define:


---
*Page 25*


what endpoints exist
what data to send
what response to expect
And they use HTTP as the underlying
communication protocol.
Now everything is starting to connect:
HTTP → how data travels
HTTPS → secure communication
APIs → how systems understand each other
👇
And that’s what we’ll explore next
APIs and Data Modules
7. APIs (Application Programming
Interfaces)
In the previous section, we saw that HTTP defines
how data is transferred.


---
*Page 26*


But that raises an important question:
How do clients know what to send… and what they’ll
get back?
That’s where APIs come in.
What is an API?
Think of an API as a middleman between the
client and the server.


---
*Page 27*


Instead of the client dealing with all the internal
logic, it simply talks to the API.
Client → API → Server
Server → API → Client
The API handles everything in between.
Why APIs are everywhere
Almost every digital service you use relies on APIs:
social media apps
e-commerce platforms
banking systems
ride-hailing apps
Behind the scenes, multiple APIs are constantly
talking to each other.
How APIs work (simple flow)
The client sends a request to an API endpoint
The API processes it:


---
*Page 28*


runs logic
interacts with databases
may call other services
The API prepares a response
It sends back structured data (usually JSON or
XML)
The client then displays that data to the user.
Why APIs are powerful
APIs provide abstraction.
Which means:
the client doesn’t need to know how things work
internally
it just needs to know:
what to request
what response it will receive


---
*Page 29*


👉
“Ask for data → get data → display it”
That’s it.
Now everything connects even better:
HTTP → how data travels
HTTPS → secure communication
APIs → how systems interact
And now comes an interesting question:
What different styles or patterns can APIs follow?
8. REST API
In the previous section, we learned what APIs are.
Now the next question is:
How are APIs actually designed?
There are different styles… but the most popular
one is:


---
*Page 30*


REST (Representational State Transfer)
What is REST?
REST is a set of rules and conventions that define
how clients and servers communicate over HTTP
in a clean and structured way.
It’s simple, predictable, and widely used across
almost every modern web application.
Core ideas behind REST
1. Stateless


---
*Page 31*


Each request is independent.
The server does not remember previous
requests
Every request must contain all the necessary
information
No memory between requests
2. Resource-Based
In REST, everything is treated as a resource.
Examples:
/users
/orders
/products
Each URL represents a specific piece of data.
3. Uses Standard HTTP Methods
REST uses HTTP methods to define what action
you want to perform:


---
*Page 32*


GET → retrieve data
(e.g., fetch a user profile)
POST → create new data
(e.g., add a new user)
PUT / PATCH → update existing data
(e.g., update user details)
DELETE → remove data
(e.g., delete an account)
Why REST is so popular
REST APIs are:
simple to understand
easy to scale
widely supported
cache-friendly
This is why most APIs you see today follow REST.
But REST has limitations


---
*Page 33*


As applications grow more complex, REST starts to
show some problems:
sometimes it returns more data than needed
sometimes it returns less data than needed
clients may need to make multiple requests to
gather all data
This leads to inefficient network usage and slower
performance.
What came next?
To solve these problems, a new approach was
introduced:
GraphQL (by Facebook in 2015)
And it changes how clients request data
completely.
👇
Let’s understand that next
9. GraphQL


---
*Page 34*


In the previous section, we saw the limitations of
REST:
too many requests
too much or too little data
So the question became:
What if the client could ask for exactly what it needs?
That’s exactly what GraphQL solves.
What is GraphQL?
Unlike REST, where the server decides the
structure of the response…
GraphQL lets the client decide what data it wants


---
*Page 35*


Nothing more. Nothing less.
REST vs GraphQL (simple example)
Let’s say you need:
user details
profile info
recent posts
With REST, you might need multiple requests:
GET /users/123


---
*Page 36*


GET /users/123/profile
GET /users/123/posts
That’s 3 separate requests.
With GraphQL, you can fetch everything in one
single query:
“Give me user info, profile, and posts — all together”
And the server responds with exactly those fields.
Why GraphQL is powerful
reduces number of requests
avoids unnecessary data
gives full control to the client
improves efficiency and performance
One request. Exact data. Cleaner communication.
Simple way to remember
REST → server decides the response


---
*Page 37*


GraphQL → client decides the response
Now your system design knowledge is leveling up:
REST → structured and simple
GraphQL → flexible and efficient
And this brings us to the next big question:
How do we handle massive traffic when millions of
users hit our system at the same time?
10. Databases
So far, we’ve seen how clients send requests and
servers process them.
But here’s a key question:
Where does all the data actually live?
Why we need databases
If your application handles very small data, you
could store it in memory.


---
*Page 38*


But real-world applications deal with massive
amounts of data:
user information
transactions
posts, messages, logs
And memory alone isn’t enough to handle this
reliably.
That’s why we use a database.


---
*Page 39*


What is a database?
A database is a system designed to:
store data
retrieve data
manage data efficiently
It acts as the backbone of any application.
How it fits into the system
When a client makes a request:
1. The request goes to the server
2. The server communicates with the database
3. The database returns the required data
4. The server sends it back to the client
Client → Server → Database → Server → Client
Why databases matter
A good database ensures:


---
*Page 40*


reliability (data doesn’t get lost)
consistency (data stays correct)
security (data is protected)
durability (data survives failures)
Not all databases are the same
Different applications have different needs:
some need high scalability
some need strong consistency
some need fast performance at scale
Choosing the right database becomes a critical
design decision.
And this leads to the next important question:
What different types of databases exist, and when
should we use them?
11. SQL vs NoSQL
Now that we understand what databases are…


---
*Page 41*


how do we choose the right one?
There are two major types:
SQL databases
NoSQL databases
Let’s break them down.
SQL Databases (Structured & Reliable)
SQL databases store data in tables with a fixed
structure (schema).


---
*Page 42*


They follow something called ACID properties,
which ensure reliability:
Atomicity → everything succeeds or nothing
does
Consistency → data always remains valid
Isolation → transactions don’t affect each other
Durability → data is safe even after crashes
In simple terms: SQL = safe and predictable
When to use SQL?
SQL is best when:
your data is structured
relationships between data are important
you need strong consistency
Examples:
banking systems
payment systems


---
*Page 43*


order management
Popular databases:
MySQL, PostgreSQL
NoSQL Databases (Flexible & Scalable)
NoSQL databases are designed for scale and
flexibility.
They don’t require a fixed schema and can handle
large, distributed data efficiently.
There are different types:
Key-Value → super fast lookups (e.g., Redis)
Document → JSON-like flexible data (e.g.,
MongoDB)
Graph → relationships-heavy data (e.g., Neo4j)
Wide-Column → large-scale distributed systems
(e.g., Cassandra)
In simple terms: NoSQL = flexible and fast at scale


---
*Page 44*


SQL vs NoSQL (quick intuition)
SQL → structured + consistent
NoSQL → flexible + scalable
So… which one should you choose?
It depends on your system needs:
Need strong consistency & relationships → SQL
Need high scalability & flexible data → NoSQL
Real-world approach
Modern systems don’t choose one.
They use both.
For example, an e-commerce app might:
store orders in SQL (because accuracy matters)
store recommendations in NoSQL (because
speed & flexibility matter)
Now your system is getting more powerful:


---
*Page 45*


APIs → communication
Databases → storage
SQL/NoSQL → choosing the right storage
Which brings us to the next challenge:
How do we make data access faster as traffic grows?
Scaling and Performance
12. Vertical Scaling (Scaling Up)
As your application grows, more users start hitting
your server.
At first, a single server might handle everything
just fine.
But over time…
it becomes a bottleneck


---
*Page 46*


Requests pile up, response times increase, and the
system starts slowing down.
The quick solution
The simplest fix is:
make the server more powerful
add more CPU
add more RAM
increase storage
This approach is called:
Vertical Scaling (Scaling Up)


---
*Page 47*


You’re not changing the system architecture
you’re just upgrading the same machine.
Why vertical scaling doesn’t scale well
It works… but only up to a point.
1. Hardware limits
Every machine has a maximum capacity.
You can’t upgrade forever.
2. Cost increases fast
Stronger machines are much more expensive.


---
*Page 48*


Cost doesn’t grow linearly — it grows
exponentially.
3. Single Point of Failure (SPOF)
Everything depends on one server.
If it crashes:
your entire system goes down
Simple way to think
Vertical scaling = making one machine stronger
But still relying on one machine
So what’s the better approach?
Instead of making one machine bigger…
what if we used multiple machines together?
That’s where the next concept comes in
and it completely changes how systems are
👇
designed at scale
13. Horizontal Scaling (Scaling Out)


---
*Page 49*


In the previous section, we saw the limitations of
vertical scaling.
So instead of making one server more powerful…
what if we simply add more servers?
What is Horizontal Scaling?
Horizontal scaling means:
adding more machines to share the workload


---
*Page 50*


Instead of:
one big server
You now have:
multiple smaller servers working together
This is called:
Horizontal Scaling (Scaling Out)
Why horizontal scaling is better
1. More servers = more capacity
As traffic grows, you can simply add more servers.
your system grows with your users
2. No Single Point of Failure
If one server crashes:
others continue handling requests
This makes your system much more reliable


---
*Page 51*


3. Cost-effective
Instead of buying one expensive machine:
you use multiple affordable ones
This is often cheaper and more flexible.
Simple way to think
Vertical Scaling → make one server stronger
Horizontal Scaling → add more servers
Scale up vs Scale out
But this creates a new problem
Now you have multiple servers…
how does a client know which server to connect to?
Because if every client randomly hits servers,
things can get messy.
The solution
We need something that:


---
*Page 52*


distributes traffic
balances load
ensures no server gets overwhelmed
That’s where a Load Balancer comes in.
And this is one of the most important components
👇
in scalable systems
14. Load Balancers
In the previous section, we added multiple servers
to handle more traffic.
But that created a new problem:
How do we decide which server should handle each
request?
What is a Load Balancer?
A Load Balancer sits between the client and your
servers.


---
*Page 53*


It acts like a traffic manager
Instead of clients directly hitting servers:
Client → Load Balancer → Server
The load balancer receives all incoming requests
and distributes them across multiple servers.
Why Load Balancers are important
1. Better performance
Traffic is distributed evenly.


---
*Page 54*


no single server gets overloaded
2. High availability
If one server crashes:
the load balancer automatically redirects traffic
to healthy servers
Your system keeps running.
3. Scalability
As you add more servers:
the load balancer continues distributing traffic
seamlessly
How does it decide where to send requests?
Load balancers use different algorithms:
Round Robin
Requests are sent one by one in order:
Server A → Server B → Server C → repeat
simple and evenly distributed


---
*Page 55*


Least Connections
Requests go to the server with the fewest active
connections.
better for uneven workloads
IP Hashing
Requests from the same user (same IP) go to the
same server.
useful for maintaining session consistency
Simple way to think
Load Balancer = smart traffic controller
It ensures:
fairness
reliability
smooth performance
Now your system is becoming truly scalable:


---
*Page 56*


Horizontal scaling → multiple servers
Load balancer → smart traffic distribution
Which leads to the next challenge:
How do we reduce the load on servers even further
and make responses faster?
15. Database Indexing
As your application grows, your database starts
handling more and more queries.
And at some point, you’ll notice something:
queries are getting slower
The simple solution: Indexing


---
*Page 57*


One of the fastest ways to improve read
performance is:
indexing
Think of it like the index page at the back of a
book.
Instead of flipping through every page…
you jump directly to the exact section you need.
How indexing works


---
*Page 58*


A database index is like a shortcut.
It stores:
column value
along with pointers to the actual data rows
So instead of scanning the entire table:
the database directly jumps to the required data
Where should we use indexes?
Indexes are usually created on columns that are
frequently searched:
Primary keys
Foreign keys
columns used in WHERE conditions
basically, anything you query often
Simple way to think


---
*Page 59*


Index = faster reads
But slightly slower writes
When should you use it?
Only index:
frequently queried columns
high-impact queries
Don’t index everything — be intentional
But what if indexing isn’t enough?
As traffic keeps growing, even a well-indexed
database can struggle with too many read requests.
So the next question is:
What if we could distribute reads across multiple
databases?
👇
That’s exactly what Replication helps us do
16. Replication


---
*Page 60*


Earlier, we scaled our application by adding more
servers.
Now the question is:
Can we do the same for databases?
Yes and that’s called Replication.
What is Replication?
Replication means:
creating multiple copies of the same database


---
*Page 61*


These copies run on different servers but contain
the same data.
How it works
In a typical setup, we have:
Primary Database (Master)
Handles all write operations
(INSERT, UPDATE, DELETE)
Read Replicas
Handle read operations
(SELECT queries)
Whenever data is written to the primary database:
it is copied to all replicas
So all databases stay in sync.
Why replication is powerful
1. Improved read performance
Instead of one database handling all reads:


---
*Page 62*


multiple replicas share the load
2. Better availability
If the primary database fails:
a replica can be promoted as the new primary
Your system keeps running.
Simple way to think
One database for writing
Multiple databases for reading
But replication has a limitation
Replication helps a lot with read scaling…
But:
writes still go to a single primary database
Which means:
write traffic can become a bottleneck
storage is still limited to one dataset


---
*Page 63*


So what if we need more?
What if:
we have huge amounts of data
or extremely high write traffic
we need to split the data itself
And that’s where the next concept comes in:
Sharding
Data Management
17. Sharding (Horizontal Partitioning)
At some point, your application grows a lot.
millions of users
massive traffic
terabytes of data


---
*Page 64*


And now your database starts struggling.
A single database server is no longer enough.
The idea: Split the data
Instead of storing everything in one place…
we split the database into smaller pieces
and distribute them across multiple servers.
This technique is called:
Sharding


---
*Page 65*


How sharding works
We divide the database into smaller parts called:
shards
Each shard:
contains a subset of the total data
runs on a separate server
How is data distributed?
Data is split based on a sharding key.
For example:
user ID
region
customer ID
So instead of one database storing all users:
Shard 1 → Users 1–1M
Shard 2 → Users 1M–2M


---
*Page 66*


Shard 3 → Users 2M–3M
each shard handles only its portion of data
Why sharding is powerful
1. Reduced load
Each database handles only a part of the data.
less pressure on a single server
2. Better performance
Queries are distributed across shards.
faster reads and writes
3. Scalability
As data grows:
you can simply add more shards
Simple way to Learn
Replication = copy the same data
Sharding = split the data
Important note


---
*Page 67*


Sharding is also called:
Horizontal Partitioning
Because we split data by rows.
But what if the problem is different?
So far, we split data by rows.
But what if:
the issue isn’t too many rows
but too many columns in a table?
In that case, we use a different technique:
Vertical Partitioning
Let’s explore that next
18. Vertical Partitioning
In the previous section, we split data by rows using
sharding.


---
*Page 68*


But what if the problem isn’t too many rows…
what if the table itself has too many columns?
The problem
Imagine a User table that stores everything:
profile details (name, email, profile picture)
login history (last login, IP addresses)
billing information (address, payment details)
As this table grows, something happens:
queries become slower
Because even if you only need a few fields…
the database still scans a large, heavy table
The solution: Vertical Partitioning


---
*Page 69*


Instead of splitting by rows…
we split the table by columns
This is called:
Vertical Partitioning
How it works
We break one large table into smaller, focused
tables:
User_Profile → name, email, profile picture


---
*Page 70*


User_Login → login timestamps, IP addresses
User_Billing → billing address, payment details
Each table now stores only related data.
Why this improves performance
1. Faster queries
Each request only scans relevant columns.
less data to process
2. Reduced disk I/O
Smaller tables = less data read from disk.
faster data retrieval
Simple way to think
Sharding → split by rows
Vertical Partitioning → split by columns
Row split vs Column split
But there’s still a limit
No matter how much we optimize databases…


---
*Page 71*


reading from disk is always slower than memory
So what if we go faster?
What if we store frequently accessed data in
memory…
for near-instant access?
That’s exactly what Caching solves
19. Caching
So far, we’ve optimized our database in multiple
ways.
But there’s still one limitation:
reading from disk is slow
Even the best-optimized database can’t match the
speed of memory.
The idea: Store data closer to the application
Instead of fetching data from the database every
time…


---
*Page 72*


we store frequently accessed data in memory
This is called:
Caching
Why caching is powerful
memory is much faster than disk
reduces load on the database
improves response time significantly
same data, much faster access


---
*Page 73*


Cache Aside Pattern (most common)
The most widely used caching strategy is:
Cache Aside
Here’s how it works:
1. User requests data
2. Application checks the cache first
If data is in cache (Cache Hit)
return it instantly
(no database call needed)
If data is not in cache (Cache Miss)
fetch data from the database
store it in the cache
return it to the user
Next time the same data is requested:
it comes directly from cache (super fast)
Keeping cache fresh (TTL)


---
*Page 74*


One problem with caching is:
data can become outdated
To solve this, we use:
TTL (Time-To-Live)
each cached item has an expiration time
after that, it is automatically removed or
refreshed
Simple way to think
Cache = shortcut to frequently used data
Popular tools
Redis
Memcached
But what if users are globally distributed?
Caching works great within a system…
But what if users are spread across the world and
need fast access to static content like images,


---
*Page 75*


videos, and assets?
That’s where CDNs (Content Delivery Networks)
👇
come in
20. Denormalization
In most relational databases, we follow a principle
called Normalization.
It means splitting data into multiple tables to
reduce duplication.
The problem with normalization
Let’s take a simple example of a blog platform:
Users → stores user info (name, email)
Posts → stores blog posts
Comments → stores comments
Now imagine you want to show:
a post along with the author’s name and all comments


---
*Page 76*


The database has to perform multiple JOIN
operations to combine data from different tables.
As your data grows…
these joins become slower and more expensive
The idea: Denormalization
Instead of keeping everything separate…
we combine related data into a single table


---
*Page 77*


This is called:
Denormalization
Example (Denormalized)
Instead of separate tables, we might store:
post title
author name
comment text
all together in one place
So when we fetch data:
no JOINs needed
Why denormalization is useful
1. Faster reads
Data is already combined.
no need for complex joins
2. Better performance for read-heavy systems


---
*Page 78*


Perfect for:
dashboards
feeds (like social media)
analytics systems
The trade-offs
Denormalization comes with a cost:
data duplication (same data stored multiple
times)
more storage usage
complex updates (you need to update data in
multiple places)
Simple way to think
Normalization → less duplication, more joins
Denormalization → more duplication, fewer
joins
Clean data vs Fast reads
When should you use it?


---
*Page 79*


when your system is read-heavy and performance
matters more than storage
Now your system is becoming highly optimized:
Indexing → faster lookups
Replication → scale reads
Sharding → scale data
Caching → faster access
Denormalization → faster queries
Which leads to the next question:
How do we handle failures and make our system
reliable at scale?
Distributed System
21. CAP Theorem


---
*Page 80*


As our system grows and spreads across multiple
servers and data centers…
we enter the world of distributed systems
And here, things get tricky.
The big challenge
When your system is distributed, you want three
things:
Consistency (C)→ always get the latest data
Availability (A) → system always responds
Partition Tolerance (P) → system keeps working
even if network breaks
Sounds ideal, right?
But here’s the reality:
You can’t have all three at the same time
This is called the CAP Theorem.


---
*Page 81*


Understanding the trade-off
In distributed systems, network failures are
inevitable.
So Partition Tolerance (P) is non-negotiable.
That means you must choose between:
CP (Consistency + Partition Tolerance)
always return the latest data
but may reject requests during failures


---
*Page 82*


correct but sometimes unavailable
Example:
traditional SQL systems (like MySQL setups)
AP (Availability + Partition Tolerance)
system always responds
but data might be slightly outdated
always available, but not always perfectly consistent
Example:
NoSQL systems (like Cassandra, DynamoDB)
What is Eventual Consistency?
In AP systems, we use:
Eventual Consistency
Instead of updating everything instantly:
one node gets updated first


---
*Page 83*


system immediately responds (fast!)
changes are propagated to other nodes
asynchronously
After a short time:
all nodes become consistent
Simple example
User updates profile on one server
system instantly says “updated”
other servers update in the background
after a few seconds → all servers match
Simple way to think
Consistency → always correct data
Availability → always get a response
Partition Tolerance → system survives network
failures
Pick 2 (because P is mandatory)


---
*Page 84*


Real-world intuition
Banking systems → prefer Consistency (CP)
Social media feeds → prefer Availability (AP)
Now your system design thinking is getting deeper:
scaling → replication, sharding
performance → caching, indexing
trade-offs → CAP theorem
Which leads to the next question:
How do we design systems that remain reliable even
when things fail?
22. Blob Storage
So far, we’ve mostly talked about storing structured
data like users, orders, and records.
But modern applications deal with much more
than that:


---
*Page 85*


images
videos
PDFs
audio files
large, unstructured data
The problem
Traditional databases are not designed to handle
these large files efficiently.
they become slow
storage becomes expensive
performance degrades
The solution: Blob Storage


---
*Page 86*


Instead of storing files in a database…
we use Blob Storage
Blob = Binary Large Object
These are simply large files like images, videos, or
documents.
How it works
Files (blobs) are stored in containers/buckets
Each file gets a unique URL


---
*Page 87*


You can access it directly over the internet
Example:
https://your-bucket.s3.amazonaws.com/images/profile.p
Why Blob Storage is powerful
1. Massive scalability
It can store petabytes of data without any issues.
2. Cost-efficient
pay only for what you use
No need to manage expensive database storage.
3. Built-in durability
Data is automatically:
replicated
distributed across multiple locations
very low risk of data loss


---
*Page 88*


4. Easy access
Files can be accessed via:
direct URLs
APIs
Perfect for serving media content.
Real-world use case
Streaming:
videos
audio
large media files
Directly from blob storage to users.
But there’s a challenge
If your users are far from the storage location:
file delivery can become slow
Especially for large media content.


---
*Page 89*


So what’s the solution?
What if we could serve files from locations closer to
users?
That’s exactly what CDNs (Content Delivery
👇
Networks) solve
23. CDN (Content Delivery Network)
Imagine this:
You’re in India trying to watch a video
But the server is located in California
Every time you press play:
data travels across the globe
latency increases
buffering starts
The problem
Serving content from a single location is slow for
global users.


---
*Page 90*


The farther the user is from the server:
the slower the experience
The solution: CDN
A Content Delivery Network (CDN) solves this
problem.
It’s a network of servers distributed across the
world
How it works


---
*Page 91*


Instead of serving content from one central server:
CDN stores (caches) content on multiple edge
servers
these servers are located closer to users globally
What happens when a user requests content?
1. User sends a request
2. CDN finds the nearest edge server
3. Content is served from that nearby server
no need to travel across the world
Why CDN is powerful
1. Faster load times
Content comes from the closest location
minimal delay
2. Reduced latency
Shorter distance = faster data transfer
3. Better user experience


---
*Page 92*


faster page loads
smooth video streaming
less buffering
4. Reduced load on origin server
CDN handles most requests
your main server stays less stressed
Simple way to think
CDN = content closer to users
Real-world example
Platforms like:
YouTube
Netflix
Instagram
All use CDNs to deliver content globally.
Now your system is becoming truly global:


---
*Page 93*


Blob Storage → store large files
CDN → deliver them fast worldwide
Which leads to the next challenge:
How do we make systems reliable and fault-tolerant
at scale?
24. WebSockets
So far, most communication we’ve seen follows the
HTTP request–response model.
Client sends a request
Server responds
Connection closes
If the client needs new data:
it has to send another request
The problem
This works fine for normal applications…


---
*Page 94*


But not for real-time systems like:
live chat apps
stock market dashboards
multiplayer games
Why HTTP struggles with real-time
To simulate real-time updates, we use polling:
the client keeps asking the server every few
seconds:
“Any new data?”
“Any new data?”
“Any new data?”
Most of the time:
the answer is nothing new
Which leads to:
unnecessary requests


---
*Page 95*


wasted bandwidth
increased server load
The solution: WebSockets
WebSockets change the model completely.
Instead of repeated requests…
we create a persistent connection
How WebSockets work
1. Client establishes a WebSocket connection


---
*Page 96*


2. Connection stays open
3. Both sides can send data anytime
full two-way communication
Why WebSockets are powerful
no need for repeated requests
instant updates
lower latency
efficient communication
Simple way to think
HTTP → ask again and again
WebSocket → stay connected and talk anytime
Real-world use cases
chat applications
live notifications
real-time dashboards
gaming
But what about server-to-server communication?


---
*Page 97*


WebSockets are great for client ↔ server
communication.
But what if:
one server needs to notify another server?
Example
Payment happens → payment service should
notify your backend
Code pushed → CI/CD pipeline should trigger
automatically
👇
This is where Webhooks come in
25. Webhooks
In the previous section, we saw how WebSockets
enable real-time communication between a client
and a server.
But what if:
one server needs to notify another server?


---
*Page 98*


The problem
Without webhooks, your system would need to
keep checking:
“Did something happen?”
“Did something happen?”
This is called polling and it’s inefficient.
wastes resources
increases API calls
most requests return nothing
The solution: Webhooks


---
*Page 99*


Instead of constantly asking…
Webhooks let the server notify you instantly
How Webhooks work
1. Your application provides a webhook URL
2. You register this URL with a provider
(e.g., Stripe, GitHub, Twilio)
3. When an event happens:


---
*Page 100*


the provider sends an HTTP POST request
to your webhook URL with event data
4. Your application receives it and processes it:
update database
trigger workflows
send notifications
Why Webhooks are powerful
no polling needed
real-time event delivery
fewer API calls
efficient resource usage
Simple way to think
Polling → keep asking
Webhooks → get notified
“Don’t call me, I’ll call you”
Real-world examples


---
*Page 101*


Payment completed → Stripe notifies your
backend
Code pushed → GitHub triggers CI/CD
Message received → Twilio sends webhook
Now your system supports real-time workflows:
WebSockets → real-time client communication
Webhooks → real-time server-to-server events
Which leads to the next challenge:
How do we handle tasks that don’t need to be
processed immediately?
Advanced and Reliability
26. Microservices
So far, we’ve been scaling different parts of our
system…


---
*Page 102*


But what about the application itself?
The traditional approach: Monolith
Earlier, applications were built as a monolith.
everything lives in one single codebase:
authentication
payments
orders
inventory
shipping
All tightly connected.
The problem with monoliths
This works fine at small scale…
But as the system grows, problems start appearing:
Hard to scale → you must scale the entire app,
even if only one part needs it


---
*Page 103*


Risky deployments → one small bug can break
the whole system
Tightly coupled → failure in one module can
affect everything
Example
Imagine an e-commerce app:
if the inventory service crashes
the entire application might go down
The solution: Microservices


---
*Page 104*


Instead of one big system…
we break it into smaller, independent services
This is called:
Microservices Architecture
How microservices work
Each microservice:
handles a single responsibility
(e.g., payments, orders, users)
has its own logic and database
communicates with other services via:
APIs
or message queues
Why microservices are powerful
1. Independent scaling
Only scale what’s needed.


---
*Page 105*


no need to scale the entire system
2. Safer deployments
Update one service without affecting others.
3. Better fault isolation
If one service fails:
others can continue working
Simple way to think
Monolith → one big system
Microservices → many small systems working
together
Divide and scale
But there’s a challenge
Now we have multiple services…
they need to communicate with each other
Direct API calls can become:
slow


---
*Page 106*


tightly coupled
hard to manage
So what’s the solution?
What if services could communicate asynchronously
and reliably?
👇
That’s where Message Queues come in
27. Message Queues
In a monolithic system, components usually talk to
each other directly:
one function calls another and waits for a
response
This is called synchronous communication.
The problem in microservices
In a microservices system, this approach breaks
down:
if one service is slow → everything slows down


---
*Page 107*


if one service is down → requests fail
high traffic → services get overloaded
waiting for responses doesn’t scale well
The solution: Message Queues
Instead of direct communication…
services communicate through a Message Queue
This enables:


---
*Page 108*


asynchronous communication
How it works
1. A producer sends a message
(e.g., “Process Payment”)
2. The message is placed in a queue
3. A consumer picks it up when ready
4. The task is processed independently
Flow example
Checkout service → sends payment request
Message Queue → stores it
Payment service → processes it when available
no waiting, no blocking
Why message queues are powerful
1. Decoupling
Services don’t depend on each other directly.
more flexible architecture


---
*Page 109*


2. Better scalability
Services can process messages at their own pace.
3. Fault tolerance
If a service is down:
messages stay in the queue and are processed later
4. Load management
Queues act as a buffer during traffic spikes.
prevents system overload
Simple way to think
Message Queue = task waiting line
Popular tools
Apache Kafka
RabbitMQ
Amazon SQS
Now your system can handle heavy internal
workloads:


---
*Page 110*


Microservices → modular architecture
Message Queues → async communication
But there’s still one challenge:
How do we prevent external users from overwhelming
our system?
👇
That’s where Rate Limiting comes in
28. Rate Limiting
Imagine this:
a bot starts sending thousands of requests per
second to your system
Without any control, this can:
crash your servers
increase cloud costs
slow down the app for real users
The solution: Rate Limiting


---
*Page 111*


Rate Limiting controls how many requests a client
can make within a time window
It ensures that no single user (or bot) can
overwhelm your system.
How it works
Each user/IP gets a request quota
(e.g., 100 requests per minute)
If the limit is exceeded:
server temporarily blocks further requests


---
*Page 112*


returns:
HTTP 429 → Too Many Requests
Why rate limiting is important
protects against abuse & bots
prevents system overload
ensures fair usage for all users
controls infrastructure cost
Common algorithms
Fixed Window
limit requests in a fixed time block
(e.g., 100 per minute)
simple but can allow sudden bursts
Sliding Window
dynamically adjusts limits over time
smoother traffic handling
Token Bucket
users get tokens over time


---
*Page 113*


each request consumes a token
allows controlled bursts + steady flow
Simple way to think
Rate Limiting = traffic control for your APIs
Do we build this ourselves?
Not usually.
In real systems, rate limiting is handled by:
API Gateways
They sit in front of your services and manage:
request limits
authentication
routing
Now your system is getting production-ready:
Message Queues → handle internal load
Rate Limiting → control external traffic


---
*Page 114*


Which leads to the next layer:
How do we manage and secure all incoming API
requests efficiently?
29. API Gateway
By now, your system has:
multiple microservices
rate limiting
authentication needs
traffic coming from everywhere
Now imagine exposing all those services directly…
it would be messy, insecure, and hard to manage
The solution: API Gateway


---
*Page 115*


An API Gateway acts as a single entry point for all
client requests.
Instead of:
Client → multiple services
We now have:
Client → API Gateway → Services
How it works
1. Client sends a request to the API Gateway


---
*Page 116*


2. The gateway performs checks:
authentication
rate limiting
request validation
3. It routes the request to the correct microservice
4. The response comes back through the gateway
to the client
Why API Gateways are powerful
1. Centralized control
All important logic is handled in one place:
authentication
rate limiting
logging
2. Improved security
Services are not exposed directly


---
*Page 117*


everything goes through the gateway
3. Simplified architecture
Clients don’t need to know:
how many services exist
where they are
they just call one endpoint
4. Better scalability
Gateway manages traffic efficiently across
services.
Simple way to think
API Gateway = front door of your system
Popular tools
NGINX
Kong
AWS API Gateway
Now your system architecture is almost complete:


---
*Page 118*


Microservices → modular design
Message Queues → async processing
Rate Limiting → traffic control
API Gateway → centralized access
Which leads to the final piece:
How do we monitor, debug, and maintain such
complex systems?
30. Idempotency
As systems become distributed, one thing is
guaranteed:
failures and retries will happen
The problem
Imagine this:
a user clicks “Pay Now”
network is slow…
user refreshes the page


---
*Page 119*


Now your system might receive:
2 identical payment requests
Without proper handling:
the user could be charged twice
The solution: Idempotency
Idempotency ensures:
multiple identical requests = same result as one
request


---
*Page 120*


No matter how many times the request is
repeated…
the outcome stays the same
How it works
1. Each request gets a unique ID
(e.g., request_1234)
2. Before processing, the system checks:
“Have I already processed this request?”
If YES → ignore it (or return previous result)
If NO → process it normally
Why idempotency is critical
prevents duplicate payments
ensures data consistency
handles retries safely
makes systems reliable under failure
Simple way to think
Do it once… even if it’s called multiple times


---
*Page 121*


Real-world use cases
payment systems
order creation
booking systemsh
API retries
Final connection
Now everything you’ve learned comes together:
scaling → horizontal scaling, load balancers
data → databases, caching, sharding
communication → APIs, WebSockets, queues
reliability → rate limiting, idempotency
This is what makes modern systems robust and
production-ready
I’m genuinely happy you’re still here


---
*Page 122*


Seriously… thank you for taking the time to read
this entire story
If I made any mistakes, please forgive me.
System Design can feel overwhelming at first I’ve
been there too.
But once you break it down into these core
concepts, it starts to feel much more logical… even
enjoyable.
These 30 concepts aren’t just theory.
They’re the same building blocks used in real-
world systems the kind of systems you use every
day.
If you truly understand them, you’re already ahead
of most developers.
Now it’s your turn
Don’t just read this…


---
*Page 123*


try to connect these concepts
try to visualize real systems
try to build something small using them
That’s where real learning happens.
If this story helped you even a little:
give it a clap
share it with your developer friends
and tell me in the comments which concept
clicked the most for you?
I read every comment, and I’d love to know your
thoughts.
☕
Support my work
If you want to support what I’m doing, you can buy
me a coffee here:
Sachin
󰞵
Full Stack Developer | Tech Blog WriterI'm
i t F ll St k D l kill d i


---
*Page 124*


buymeacoffee.com
❤
No pressure at all — your support means a lot
Thanks again for reading.
See you in the next story
Editor’s Note : AI tools helped me refine and structure
parts of this story and create images . However, the
story, the conversations, and the opinions shared here
are entirely my own. AI simply helped me
communicate these ideas more clearly.I believe in
being transparent about the tools I use while writing.
😊
System Design Concepts Programming
Software Engineering Artificial Intelligence
System Design Interview


---
*Page 125*


Published in Let’s Code Future
Follow
11.4K followers · Last published 17 hours ago
🚀
Welcome to Let’s Code Future! We share stories on
Software Development, AI, Productivity, Self-
Improvement, and Leadership to help you grow,
innovate, and stay ahead. join us in shaping the future
— one story at a time!
Written by Deep concept
Following
2.2K followers · 481 following
No responses yet
To respond to this story,
get the free Medium app.
More from Deep concept and Let’s Code
Future


---
*Page 126*


In by In by
Let’s Code Fut… Deep conc… Engineerin… The Unwritte…
After 5000+ Failed I Replaced Our Senior
P t I Fi ll E i ith AI Th
Copy this now $180K salary saved. $2.1M in
l t d ti it T t
Jan 2 Mar 19
In by In by
Let’s Code F… coding with … Let’s Code Fut… Deep conc…
The Data Science My 10 Productivity
P tf li Th t G t M H k Th t M k
Not because I was a genius — You can apply most of these
b t b I fi ll t d t d if ’ l d
Dec 15, 2025 Jan 10
See all from Deep concept See all from Let’s Code Future


---
*Page 127*


Recommended from Medium
In by Code With Sunil | Code Smarter, …
Write A Catal… 𝐍𝐀𝐉𝐄𝐄𝐁…
Forget ChatGPT &
6 Boring Micro SaaS
G i i? H A th
Ni h Th t C ld
You’ve probably never heard
The overlooked business
f t f th AI t l
i h h i l ft
Mar 22 Mar 24


---
*Page 128*


In by Tushar Kanjariya
Code Like A … Alina Kovtun…
Four Lines in <head>
Concurrency,
Ch d M Sit
P ll li d A
The browser just needed a
A guide to how modern
hi t
ft h dl lti l
Mar 25 Mar 20
In by Vinod Pal
Javarevisited Gopi C K
AI Was Supposed to
5 Developer Skills That
R l D l b
Will M tt M Th
Turns out, replacing
Introduction: The Shift No One
d l i h d th
C I
Mar 27 Mar 28
See more recommendations