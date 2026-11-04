"""
Rich Question Bank Seeder for EduMateAI
Populates 54 curated, multi-domain questions across 6 subjects and 3 difficulty tiers (Easy, Medium, Hard).
"""

import os
import sys

# Ensure project root is importable when executed directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CURRICULUM_DATASET = [
    # =========================================================
    # 1. Python Programming (9 Questions: 3 Easy, 3 Medium, 3 Hard)
    # =========================================================
    {
        "topic": "Python Programming", "difficulty": "Easy",
        "question": "Which of the following built-in data types in Python is immutable?",
        "options": ["A. List", "B. Tuple", "C. Dictionary", "D. Set"],
        "correct_answer": "B",
        "explanation": "Tuples are immutable sequences in Python; once created, their elements cannot be reassigned or mutated in place."
    },
    {
        "topic": "Python Programming", "difficulty": "Easy",
        "question": "What is the boolean output of `bool('False')` in Python?",
        "options": ["A. False", "B. True", "C. None", "D. ValueError"],
        "correct_answer": "B",
        "explanation": "In Python, any non-empty string has truthy value True regardless of its character contents; only the empty string '' evaluates to False."
    },
    {
        "topic": "Python Programming", "difficulty": "Easy",
        "question": "Which keyword creates an anonymous single-expression function in Python?",
        "options": ["A. func", "B. def", "C. lambda", "D. inline"],
        "correct_answer": "C",
        "explanation": "The `lambda` keyword creates small anonymous function objects limited to a single expression."
    },
    {
        "topic": "Python Programming", "difficulty": "Medium",
        "question": "What is the average-case time complexity of membership testing `x in s` when `s` is a Python `set`?",
        "options": ["A. O(1)", "B. O(n)", "C. O(log n)", "D. O(n log n)"],
        "correct_answer": "A",
        "explanation": "Python sets are backed by open-addressing hash tables, giving O(1) average lookup complexity."
    },
    {
        "topic": "Python Programming", "difficulty": "Medium",
        "question": "How does CPython reclaim memory occupied by objects involved in reference cycles?",
        "options": [
            "A. Reference counting alone",
            "B. Generational cycle-detecting garbage collector",
            "C. Manual pointer deallocation",
            "D. Stack frame unwinding only"
        ],
        "correct_answer": "B",
        "explanation": "CPython pairs immediate reference counting with a generational cyclic garbage collector (`gc` module) to detect and collect unreachable reference cycles."
    },
    {
        "topic": "Python Programming", "difficulty": "Medium",
        "question": "Why is using a mutable default argument like `def append_item(val, items=[]):` considered an anti-pattern?",
        "options": [
            "A. It raises a SyntaxError in Python 3",
            "B. Default arguments are evaluated once at function definition time and shared across calls",
            "C. Lists cannot be passed as parameters",
            "D. It forces deep-copying on every invocation"
        ],
        "correct_answer": "B",
        "explanation": "Default parameter objects are instantiated once when `def` executes, so mutating that list persists across subsequent calls that omit the argument."
    },
    {
        "topic": "Python Programming", "difficulty": "Hard",
        "question": "What does CPython's Global Interpreter Lock (GIL) specifically restrict?",
        "options": [
            "A. Multiple native threads executing Python bytecode simultaneously within a single interpreter process",
            "B. Multiple OS processes running via multiprocessing",
            "C. Non-blocking socket I/O in asyncio event loops",
            "D. C extensions releasing the lock during matrix math"
        ],
        "correct_answer": "A",
        "explanation": "The GIL serializes Python bytecode execution across threads in one CPython process, though I/O operations and C extensions like NumPy can release it."
    },
    {
        "topic": "Python Programming", "difficulty": "Hard",
        "question": "Which algorithm determines the Method Resolution Order (MRO) for multiple inheritance in Python 3?",
        "options": [
            "A. Depth-First Left-to-Right Search",
            "B. C3 Linearization",
            "C. Breadth-First Topological Sort",
            "D. Tarjan Strongly Connected Components"
        ],
        "correct_answer": "B",
        "explanation": "Python 3 uses C3 superclass linearization (`cls.__mro__`) to preserve local precedence order and monotonicity in diamond inheritance hierarchies."
    },
    {
        "topic": "Python Programming", "difficulty": "Hard",
        "question": "What is the primary memory effect of declaring `__slots__` on a Python class?",
        "options": [
            "A. It makes all class attributes read-only constants",
            "B. It replaces per-instance `__dict__` hash maps with fixed-size descriptor arrays, reducing RAM usage",
            "C. It pins objects in CPU L1 cache",
            "D. It disables inheritance for subclasses"
        ],
        "correct_answer": "B",
        "explanation": "Declaring `__slots__` avoids allocating a dynamic `__dict__` dictionary for every instance, substantially lowering memory overhead when creating millions of objects."
    },

    # =========================================================
    # 2. Artificial Intelligence & ML (9 Questions: 3 Easy, 3 Medium, 3 Hard)
    # =========================================================
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Easy",
        "question": "Which learning paradigm trains models on datasets containing explicit input features paired with ground-truth target labels?",
        "options": ["A. Unsupervised Learning", "B. Supervised Learning", "C. Reinforcement Learning", "D. Clustering"],
        "correct_answer": "B",
        "explanation": "Supervised learning maps inputs to known target outputs (classification or regression) using labeled training examples."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Easy",
        "question": "When a neural network achieves 99% accuracy on training data but only 58% accuracy on unseen validation data, what is occurring?",
        "options": ["A. Underfitting", "B. High Bias", "C. Overfitting", "D. Feature Scaling"],
        "correct_answer": "C",
        "explanation": "Overfitting happens when a model memorizes noise and specific patterns in the training set rather than generalizing to unseen data."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Easy",
        "question": "Which evaluation metric is the harmonic mean of Precision and Recall?",
        "options": ["A. ROC-AUC", "B. F1-Score", "C. Mean Absolute Error", "D. R-Squared"],
        "correct_answer": "B",
        "explanation": "The F1-Score equals `2 * (Precision * Recall) / (Precision + Recall)`, balancing false positives and false negatives on imbalanced datasets."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Medium",
        "question": "Why is the Softmax function typically applied to the output layer in multi-class classification networks?",
        "options": [
            "A. It converts raw logits into a normalized probability distribution summing to 1.0",
            "B. It sets all negative activations to zero like ReLU",
            "C. It halves the parameter count of dense layers",
            "D. It clips exploding gradients during backpropagation"
        ],
        "correct_answer": "A",
        "explanation": "Softmax exponentiates and normalizes raw class logits so each output lies in (0, 1) and all class probabilities sum to 1."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Medium",
        "question": "What is the core objective of the Discriminator network in a Generative Adversarial Network (GAN)?",
        "options": [
            "A. Sample latent Gaussian vectors to synthesize images",
            "B. Distinguish genuine training examples from synthetic samples produced by the Generator",
            "C. Compress inputs into a lower-dimensional bottleneck",
            "D. Compute K-means cluster centroids"
        ],
        "correct_answer": "B",
        "explanation": "In a GAN's minimax game, the Discriminator learns to classify real vs. generated samples while the Generator learns to fool the Discriminator."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Medium",
        "question": "How does L1 (Lasso) regularization differ from L2 (Ridge) regularization in linear models?",
        "options": [
            "A. L1 penalizes absolute weight magnitudes and can drive irrelevant feature weights to exact zero",
            "B. L1 squares weights and never produces sparse solutions",
            "C. L1 can only be used with decision trees",
            "D. L1 increases model variance intentionally"
        ],
        "correct_answer": "A",
        "explanation": "Adding `lambda * sum(|w|)` creates diamond-shaped constraint contours that encourage exact zeros, performing built-in feature selection."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Hard",
        "question": "In scaled dot-product attention `Softmax(QK^T / sqrt(d_k)) V`, why are dot products scaled by `1 / sqrt(d_k)`?",
        "options": [
            "A. To prevent large-dimension dot products from saturating Softmax into regions with vanishingly small gradients",
            "B. To enforce orthogonality on Value matrices",
            "C. To mask future tokens in causal language modeling",
            "D. To convert time complexity from O(n^2) to O(n)"
        ],
        "correct_answer": "A",
        "explanation": "As key dimension `d_k` grows, variance of `QK^T` grows proportionally to `d_k`; dividing by `sqrt(d_k)` keeps unit variance and healthy Softmax gradients."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Hard",
        "question": "In Retrieval-Augmented Generation (RAG), why is hybrid search (BM25 + dense vector embeddings) often superior to dense embeddings alone?",
        "options": [
            "A. BM25 captures exact lexical matches (IDs, acronyms, rare terms) that dense semantic vectors may smooth over",
            "B. Hybrid search eliminates the need for chunking documents",
            "C. Dense embeddings cannot run on GPUs",
            "D. BM25 translates queries into SQL automatically"
        ],
        "correct_answer": "A",
        "explanation": "Combining sparse lexical scoring (BM25) with dense semantic similarity (embeddings) via Reciprocal Rank Fusion handles both exact identifiers and conceptual paraphrases."
    },
    {
        "topic": "Artificial Intelligence & ML", "difficulty": "Hard",
        "question": "What advantage does LoRA (Low-Rank Adaptation) provide when fine-tuning Large Language Models?",
        "options": [
            "A. It freezes pretrained weights and trains small rank-decomposed matrices `A` and `B`, slashing trainable parameters and optimizer VRAM",
            "B. It retrains the tokenizer vocabulary from scratch",
            "C. It removes attention layers during inference",
            "D. It converts Transformer models into Recurrent Neural Networks"
        ],
        "correct_answer": "A",
        "explanation": "LoRA represents weight updates `Delta W = B * A` with rank `r << d`, reducing trainable parameters by orders of magnitude with zero extra inference latency once merged."
    },

    # =========================================================
    # 3. Data Structures & Algorithms (9 Questions: 3 Easy, 3 Medium, 3 Hard)
    # =========================================================
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Easy",
        "question": "Which linear data structure processes elements strictly in First-In, First-Out (FIFO) order?",
        "options": ["A. Stack", "B. Queue", "C. Max-Heap", "D. Binary Search Tree"],
        "correct_answer": "B",
        "explanation": "Queues enqueue items at the rear and dequeue from the front, preserving FIFO arrival order."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Easy",
        "question": "What is the worst-case time complexity of Binary Search on a sorted array of `n` elements?",
        "options": ["A. O(1)", "B. O(log n)", "C. O(n)", "D. O(n log n)"],
        "correct_answer": "B",
        "explanation": "Binary Search halves the remaining search interval on every comparison, taking at most `floor(log2(n)) + 1` steps."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Easy",
        "question": "Which depth-first traversal of a Binary Search Tree visits node values in non-decreasing sorted order?",
        "options": ["A. Pre-order", "B. In-order", "C. Post-order", "D. Reverse Post-order"],
        "correct_answer": "B",
        "explanation": "In-order traversal visits Left Subtree -> Node -> Right Subtree, which yields keys in sorted ascending order on any valid BST."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Medium",
        "question": "What is the auxiliary call-stack space complexity of recursive QuickSort in the average vs. worst case?",
        "options": [
            "A. O(1) in all cases",
            "B. O(log n) average case and O(n) worst case (unless tail-call optimized on smaller partition)",
            "C. O(n^2) auxiliary heap memory",
            "D. O(n log n) auxiliary array"
        ],
        "correct_answer": "B",
        "explanation": "Balanced partitions produce recursion depth O(log n), whereas degenerate pivot choices produce depth O(n)."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Medium",
        "question": "Why cannot Dijkstra's shortest-path algorithm guarantee optimal results on graphs containing negative edge weights?",
        "options": [
            "A. Priority queues cannot store negative numbers",
            "B. Dijkstra greedily finalizes the minimum-distance frontier vertex assuming future edge relaxations can never decrease distance",
            "C. Negative edges always create infinite loops",
            "D. Adjacency lists only store unsigned integers"
        ],
        "correct_answer": "B",
        "explanation": "Dijkstra's greedy invariant assumes path costs increase monotonically; negative edges violate this, requiring Bellman-Ford instead."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Medium",
        "question": "Which data structure combination achieves O(1) `get(key)` and O(1) `put(key, value)` for an LRU Cache?",
        "options": [
            "A. Singly Linked List + Binary Search Tree",
            "B. Hash Map + Doubly Linked List",
            "C. Min-Heap + Dynamic Array",
            "D. Two Stacks"
        ],
        "correct_answer": "B",
        "explanation": "A Hash Map gives O(1) node lookup by key, while a Doubly Linked List maintains recency order with O(1) node splicing and tail eviction."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Hard",
        "question": "Which structural invariant is enforced by every Red-Black Tree?",
        "options": [
            "A. Left and right subtree heights differ by at most 1 at every node",
            "B. Every simple path from a node down to any descendant NIL leaf contains the exact same number of black nodes",
            "C. Every internal node has between t and 2t children",
            "D. Recently accessed nodes are splayed to the root"
        ],
        "correct_answer": "B",
        "explanation": "Uniform black-height combined with no two consecutive red nodes guarantees height is bounded by `2 * log2(n + 1)`."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Hard",
        "question": "With both Path Compression and Union by Rank, what is the amortized time complexity per operation in a Disjoint Set Union (Union-Find) structure?",
        "options": ["A. O(log n)", "B. O(alpha(n)), the inverse Ackermann function", "C. O(sqrt(n))", "D. O(n)"],
        "correct_answer": "B",
        "explanation": "Tarjan proved Union-Find with path compression and union by rank achieves `O(alpha(n))` amortized time, which is <= 4 for all practical `n`."
    },
    {
        "topic": "Data Structures & Algorithms", "difficulty": "Hard",
        "question": "When solving 0/1 Knapsack with `n` items and integer capacity `W` via Dynamic Programming, why is `O(n * W)` considered pseudo-polynomial time?",
        "options": [
            "A. Because it uses randomized hashing",
            "B. Because `W` is exponential in the bit-length `log2(W)` needed to encode `W` in binary input",
            "C. Because recursion never terminates for prime weights",
            "D. Because space cannot be optimized below O(n^2)"
        ],
        "correct_answer": "B",
        "explanation": "Formal complexity measures runtime relative to input size in bits; `W` requires `b = log2(W)` bits, so `O(n * 2^b)` is exponential in `b`."
    },

    # =========================================================
    # 4. Web Development & Cloud (9 Questions: 3 Easy, 3 Medium, 3 Hard)
    # =========================================================
    {
        "topic": "Web Development & Cloud", "difficulty": "Easy",
        "question": "What is the exact semantic difference between HTTP `401 Unauthorized` and HTTP `403 Forbidden`?",
        "options": [
            "A. 401 means missing/invalid authentication; 403 means authenticated identity lacks permission",
            "B. 401 is a server crash; 403 is a DNS failure",
            "C. 401 applies only to POST requests; 403 applies only to GET requests",
            "D. They are completely interchangeable aliases"
        ],
        "correct_answer": "A",
        "explanation": "401 indicates the client must authenticate to get the response, whereas 403 means the server knows who the client is (or doesn't care) and refuses authorization."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Easy",
        "question": "Which HTTP response header mitigates Cross-Site Scripting (XSS) by allowlisting trusted script and asset origins?",
        "options": [
            "A. Access-Control-Allow-Origin",
            "B. Content-Security-Policy",
            "C. Cache-Control",
            "D. Accept-Encoding"
        ],
        "correct_answer": "B",
        "explanation": "`Content-Security-Policy` (CSP) restricts inline script execution and untrusted external script domains."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Easy",
        "question": "Which HTTP status code indicates that a new resource was successfully created as a result of a `POST` request?",
        "options": ["A. 200 OK", "B. 201 Created", "C. 204 No Content", "D. 304 Not Modified"],
        "correct_answer": "B",
        "explanation": "`201 Created` confirms a new subordinate resource was provisioned, typically accompanied by a `Location` header."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Medium",
        "question": "What does it mean for an HTTP method (such as `GET`, `PUT`, or `DELETE`) to be idempotent?",
        "options": [
            "A. It never modifies database records",
            "B. Executing the identical request multiple times produces the same server state effect as executing it once",
            "C. Responses are always cached forever by CDNs",
            "D. Payloads are compressed with Brotli"
        ],
        "correct_answer": "B",
        "explanation": "Idempotency guarantees safe network retries: repeating `PUT /users/42` or `DELETE /users/42` leaves the server in the same state as a single call."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Medium",
        "question": "Why do browsers send an HTTP `OPTIONS` preflight request before certain cross-origin API calls?",
        "options": [
            "A. To benchmark server latency before downloading images",
            "B. To verify via CORS headers whether the target server permits non-simple methods or custom headers from the caller's origin",
            "C. To negotiate TLS cipher suites",
            "D. To refresh expired OAuth refresh tokens"
        ],
        "correct_answer": "B",
        "explanation": "For cross-origin requests with methods like `PUT`/`DELETE` or headers like `Authorization`/`Content-Type: application/json`, browsers check `Access-Control-Allow-*` via `OPTIONS` first."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Medium",
        "question": "In Docker multi-stage builds, why do production images copy compiled artifacts into a minimal runtime stage?",
        "options": [
            "A. To strip compilers, build caches, and dev dependencies—shrinking image size and security attack surface",
            "B. Because Docker containers cannot exceed 500 MB",
            "C. To run multiple kernels inside the container",
            "D. To bypass container registry authentication"
        ],
        "correct_answer": "A",
        "explanation": "Multi-stage Dockerfiles separate the heavy build toolchain stage from a lean runtime image, reducing pull times and CVE exposure."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Hard",
        "question": "In distributed microservices, how does the Saga Pattern maintain data consistency across separate service databases without distributed locks?",
        "options": [
            "A. By coordinating sequences of local transactions paired with compensating rollback transactions on failure",
            "B. By sharing a single SQLite file over NFS",
            "C. By holding XA Two-Phase Commit locks across public REST APIs",
            "D. By disabling foreign keys globally"
        ],
        "correct_answer": "A",
        "explanation": "Sagas execute local ACID transactions per service and trigger explicit compensating actions (e.g., refund payment if inventory reservation fails) to achieve eventual consistency."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Hard",
        "question": "According to Brewer's CAP Theorem, during an active network partition (`P`) between distributed database nodes, what trade-off must architects choose between?",
        "options": [
            "A. Latency vs. Bandwidth",
            "B. Linearizable Consistency (`C`) vs. High Availability (`A`)",
            "C. Encryption vs. Compression",
            "D. Horizontal vs. Vertical Scaling"
        ],
        "correct_answer": "B",
        "explanation": "When nodes cannot communicate due to a partition, a system must either reject/block writes to preserve Consistency (CP) or serve potentially stale reads/divergent writes to maintain Availability (AP)."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Hard",
        "question": "What problem does the Circuit Breaker pattern solve in cloud-native service meshes?",
        "options": [
            "A. It prevents cascading failures by failing fast when a downstream dependency exceeds an error/timeout threshold",
            "B. It encrypts east-west gRPC payloads",
            "C. It compiles TypeScript into WebAssembly",
            "D. It balances DNS round-robin records"
        ],
        "correct_answer": "A",
        "explanation": "Tripping a circuit breaker to Open stops exhausting caller thread pools on an unhealthy downstream service and periodically probes recovery in Half-Open state."
    },

    # =========================================================
    # 5. Database Systems & SQL (9 Questions: 3 Easy, 3 Medium, 3 Hard)
    # =========================================================
    {
        "topic": "Database Systems & SQL", "difficulty": "Easy",
        "question": "In SQL, what is the key difference between the `WHERE` clause and the `HAVING` clause?",
        "options": [
            "A. `WHERE` filters individual rows before grouping; `HAVING` filters aggregated groups after `GROUP BY`",
            "B. `HAVING` works only on text columns",
            "C. `WHERE` cannot be used with `SELECT` statements",
            "D. `HAVING` executes before `FROM`"
        ],
        "correct_answer": "A",
        "explanation": "`WHERE` filters raw tuple rows prior to aggregation, whereas `HAVING` evaluates conditions over aggregate functions like `COUNT(*)` or `AVG(score)`."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Easy",
        "question": "Which SQL join returns all rows from the left table and matched rows from the right table, filling `NULL` when no right-side match exists?",
        "options": ["A. INNER JOIN", "B. LEFT OUTER JOIN", "C. CROSS JOIN", "D. NATURAL JOIN"],
        "correct_answer": "B",
        "explanation": "`LEFT JOIN` (or `LEFT OUTER JOIN`) preserves every row from the left relation even when no matching foreign key exists on the right."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Easy",
        "question": "What property does a `PRIMARY KEY` constraint enforce on a relational table column?",
        "options": [
            "A. Values must be both UNIQUE and NOT NULL",
            "B. Values must be auto-incrementing floats",
            "C. At most one NULL value is permitted",
            "D. Column values are encrypted at rest"
        ],
        "correct_answer": "A",
        "explanation": "A relational primary key uniquely identifies each tuple and forbids NULL entries."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Medium",
        "question": "A table is in Second Normal Form (2NF) and contains no transitive functional dependencies of non-prime attributes on the primary key. Which normal form has it achieved?",
        "options": ["A. 1NF", "B. 3NF (Third Normal Form)", "C. Denormalized Star Schema", "D. 0NF"],
        "correct_answer": "B",
        "explanation": "Third Normal Form (3NF) eliminates transitive dependencies (`Key -> NonKeyA -> NonKeyB`), preventing update and deletion anomalies."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Medium",
        "question": "Why are B+ Trees preferred over standard Binary Search Trees for disk-backed relational database indexes?",
        "options": [
            "A. High branching factor aligns nodes with OS disk pages, minimizing disk I/O seeks, while linked leaves accelerate range scans",
            "B. B+ Trees require zero memory to update",
            "C. B+ Trees store only string keys",
            "D. Binary Search Trees cannot enforce uniqueness"
        ],
        "correct_answer": "A",
        "explanation": "Wide fan-out keeps B+ Tree height very shallow (3-4 levels for millions of rows), matching 4KB-16KB block reads and supporting fast `BETWEEN` range scans via sibling leaf pointers."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Medium",
        "question": "How does SQL `UNION ALL` differ from `UNION` in both behavior and performance?",
        "options": [
            "A. `UNION ALL` retains duplicate rows and avoids costly sort/hash deduplication overhead",
            "B. `UNION ALL` sorts rows alphabetically by default",
            "C. `UNION` allows mismatched column counts",
            "D. `UNION ALL` performs an inner join"
        ],
        "correct_answer": "A",
        "explanation": "`UNION` deduplicates combined result sets (requiring hashing or sorting), whereas `UNION ALL` streams all rows directly with higher throughput."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Hard",
        "question": "In Multi-Version Concurrency Control (MVCC) databases like PostgreSQL, how do read transactions avoid blocking concurrent write transactions?",
        "options": [
            "A. Readers inspect consistent tuple versions visible as of their transaction snapshot rather than acquiring shared row locks",
            "B. Writes are queued in a single global mutex",
            "C. Tables are copied in full before every `SELECT`",
            "D. Foreign key checks are skipped during reads"
        ],
        "correct_answer": "A",
        "explanation": "Under MVCC, updates create new row versions tagged with transaction IDs (`xmin`/`xmax`), so readers see a point-in-time snapshot without blocking writers."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Hard",
        "question": "In Write-Ahead Logging (WAL), what guarantees Durability (`D` in ACID) if power fails immediately after `COMMIT` returns?",
        "options": [
            "A. Redo log records describing the transaction are flushed (`fsync`) to non-volatile storage before acknowledging `COMMIT`",
            "B. All B+ Tree data pages are defragmented synchronously on every `INSERT`",
            "C. Query plans are cached in RAM",
            "D. Client drivers retry transactions infinitely"
        ],
        "correct_answer": "A",
        "explanation": "Sequential WAL append + `fsync` before commit acknowledgment ensures crash recovery can replay committed changes even if dirty buffer-pool pages had not yet flushed."
    },
    {
        "topic": "Database Systems & SQL", "difficulty": "Hard",
        "question": "Given a composite B-Tree index on `(department_id, created_at)`, which query predicate CANNOT efficiently use the index's leading key order?",
        "options": [
            "A. `WHERE department_id = 10 AND created_at > '2026-01-01'`",
            "B. `WHERE department_id = 10`",
            "C. `WHERE created_at = '2026-01-01'` (omitting `department_id`)",
            "D. `WHERE department_id IN (10, 20)`"
        ],
        "correct_answer": "C",
        "explanation": "Composite B-Tree indexes follow the leftmost-prefix rule: entries are sorted first by `department_id`, then by `created_at` within each department."
    },

    # =========================================================
    # 6. Cybersecurity & Networks (9 Questions: 3 Easy, 3 Medium, 3 Hard)
    # =========================================================
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Easy",
        "question": "Why does HTTPS use TLS encryption over standard HTTP?",
        "options": [
            "A. To guarantee Confidentiality, Integrity, and Server Authentication for data in transit",
            "B. To compress HTML files by 90%",
            "C. To replace DNS resolution",
            "D. To prevent SQL syntax errors on the backend"
        ],
        "correct_answer": "A",
        "explanation": "TLS encrypts traffic against eavesdropping, verifies message integrity via MAC/AEAD, and authenticates server identity via X.509 certificates."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Easy",
        "question": "What is the primary defense against SQL Injection (`SQLi`) vulnerabilities in application code?",
        "options": [
            "A. Hiding database port numbers",
            "B. Parameterized queries (Prepared Statements) separating SQL structure from user data",
            "C. Client-side JavaScript form validation only",
            "D. Base64 encoding query parameters"
        ],
        "correct_answer": "B",
        "explanation": "Parameterized queries ensure user-supplied input is bound strictly as literal data values and never parsed as executable SQL commands."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Easy",
        "question": "Which TCP handshake sequence establishes a reliable connection between a client and server?",
        "options": [
            "A. SYN -> SYN-ACK -> ACK",
            "B. GET -> 200 OK -> FIN",
            "C. PING -> PONG -> DATA",
            "D. ARP -> DNS -> TLS"
        ],
        "correct_answer": "A",
        "explanation": "TCP's 3-way handshake synchronizes initial sequence numbers via `SYN`, `SYN-ACK`, and `ACK`."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Medium",
        "question": "Why must user passwords be hashed with a slow, salted KDF (like Argon2id or bcrypt) rather than plain `SHA-256` without a salt?",
        "options": [
            "A. Unsalted fast hashes are vulnerable to precomputed rainbow tables and billions-per-second GPU brute-force attacks",
            "B. SHA-256 outputs variable-length strings",
            "C. Salting allows administrators to decrypt passwords later",
            "D. Browsers reject SHA-256 logins"
        ],
        "correct_answer": "A",
        "explanation": "Per-user cryptographic salts defeat rainbow tables, and memory-hard/work-factor KDFs like Argon2id make mass offline cracking prohibitively expensive."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Medium",
        "question": "Which cookie attribute prevents Cross-Site Request Forgery (CSRF) by restricting cookies on cross-site subrequests, and which attribute blocks `document.cookie` theft via XSS?",
        "options": [
            "A. `SameSite=Lax/Strict` mitigates CSRF; `HttpOnly` blocks JavaScript `document.cookie` access",
            "B. `Domain` mitigates CSRF; `Path` blocks XSS",
            "C. `Max-Age` mitigates CSRF; `Expires` blocks XSS",
            "D. `Public` mitigates both"
        ],
        "correct_answer": "A",
        "explanation": "`SameSite` controls cross-site cookie transmission (mitigating CSRF), while `HttpOnly` hides session cookies from client-side JavaScript."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Medium",
        "question": "In a JSON Web Token (`JWT`) formatted as `Header.Payload.Signature`, is the `Payload` hidden from whoever holds the token in standard JWS?",
        "options": [
            "A. Yes, Base64URL is military-grade encryption",
            "B. No—JWS payloads are only Base64URL-encoded and tamper-signed, NOT encrypted (anyone with the token can decode claims)",
            "C. Only numeric claims are readable",
            "D. Only the issuing database can decode Base64URL"
        ],
        "correct_answer": "B",
        "explanation": "Standard JWTs (JWS) guarantee integrity/authenticity via signature, not confidentiality; sensitive secrets should never be placed in unencrypted JWT payloads."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Hard",
        "question": "What does Perfect Forward Secrecy (PFS) via Ephemeral Diffie-Hellman (`ECDHE`) in TLS 1.3 protect against?",
        "options": [
            "A. Compromise of a server's long-term private key in the future cannot decrypt past recorded TLS sessions",
            "B. Distributed Denial-of-Service (DDoS) volumetric floods",
            "C. Phishing domain typosquatting",
            "D. Compromised root certificate authorities issuing new certs"
        ],
        "correct_answer": "A",
        "explanation": "Because ephemeral session keys are negotiated per connection and discarded after use, stealing the server's static key later yields zero ability to decrypt archived pcaps."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Hard",
        "question": "What is a Server-Side Request Forgery (`SSRF`) vulnerability in cloud web applications?",
        "options": [
            "A. Tricking the backend server into making unintended HTTP requests to internal VPC services or cloud instance metadata endpoints (e.g., `169.254.169.254`)",
            "B. Injecting CSS stylesheets into user comments",
            "C. Overflowing a client browser's localStorage quota",
            "D. Spoofing MAC addresses on home Wi-Fi"
        ],
        "correct_answer": "A",
        "explanation": "Unvalidated URL fetchers allow attackers to pivot through the server's network identity to reach internal-only APIs or cloud IAM metadata credentials."
    },
    {
        "topic": "Cybersecurity & Networks", "difficulty": "Hard",
        "question": "In OAuth 2.0 Authorization Code Flow for public SPAs/mobile apps, how does `PKCE` (Proof Key for Code Exchange) stop authorization code interception?",
        "options": [
            "A. The client generates a random `code_verifier`, sends its hash `code_challenge` up front, and proves possession of `code_verifier` when exchanging the code for tokens",
            "B. It embeds the client secret inside public HTML",
            "C. It sends user passwords in URL query strings",
            "D. It disables TLS certificate verification"
        ],
        "correct_answer": "A",
        "explanation": "Even if an attacker intercepts the one-time authorization code, they cannot exchange it at the token endpoint without the original high-entropy `code_verifier`."
    },

    # =========================================================================
    # AWS CLOUD & AMAZON BEDROCK ARCHITECTURE (Under Web Development & Cloud)
    # =========================================================================
    {
        "topic": "Web Development & Cloud", "difficulty": "Easy",
        "question": "What level of data durability is `Amazon S3` Standard designed to provide across multiple Availability Zones?",
        "options": [
            "A. 99.999999999% (11 nines) annual durability by redundantly storing objects across >= 3 Availability Zones",
            "B. 95.0% single-disk durability in one rack",
            "C. Ephemeral RAM-only storage cleared on reboot",
            "D. Local browser IndexedDB caching only"
        ],
        "correct_answer": "A",
        "explanation": "Amazon S3 Standard synchronously replicates data across at least three geographically separated Availability Zones within an AWS Region to achieve 11 nines of durability."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Easy",
        "question": "According to the `AWS IAM` Principle of Least Privilege, how should an `Amazon EC2` instance or `AWS Lambda` function authenticate to `Amazon DynamoDB`?",
        "options": [
            "A. Assume an `IAM Role` granting short-lived STS temporary credentials scoped strictly to the required table actions",
            "B. Hardcode long-lived root account credentials inside source files",
            "C. Share a single administrator password across all microservices",
            "D. Make the DynamoDB table publicly writable without authentication"
        ],
        "correct_answer": "A",
        "explanation": "IAM Roles issue automatically rotated AWS STS temporary session tokens, eliminating static secrets in code while enforcing fine-grained resource-level permissions."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Medium",
        "question": "How can you minimize latency and database connection overhead across invocations in `AWS Lambda`?",
        "options": [
            "A. Initialize SDK clients and connection pools outside the handler function (or use `Lambda SnapStart` / `RDS Proxy`) to reuse warm execution environments",
            "B. Re-install Python packages inside the handler on every request",
            "C. Force cold starts by deleting the function after every call",
            "D. Store 50 GB video files inside environment variables"
        ],
        "correct_answer": "A",
        "explanation": "Objects initialized at module scope persist across warm invocations in the same Lambda execution environment, drastically cutting cold-start and TLS handshake overhead."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Medium",
        "question": "In an `Amazon VPC`, how do backend containers in a **Private Subnet** download OS security patches from the internet without accepting inbound public traffic?",
        "options": [
            "A. Route outbound `0.0.0.0/0` traffic from the Private Subnet to a managed `NAT Gateway` residing in a Public Subnet",
            "B. Attach an Internet Gateway directly to each private container without security groups",
            "C. Disable all VPC route tables permanently",
            "D. Assign public IPv4 addresses and open port `0-65535` inbound"
        ],
        "correct_answer": "A",
        "explanation": "A NAT Gateway translates outbound private IPv4 requests to an Elastic IP via the Public Subnet's Internet Gateway while dropping unsolicited inbound connections."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Hard",
        "question": "When building an enterprise AI agent with `AWS Strands` and `Amazon Bedrock`, how do `Bedrock Knowledge Bases` and `Bedrock Guardrails` collaborate?",
        "options": [
            "A. Knowledge Bases ground responses via managed vector retrieval (`RAG`) with citations, while Guardrails enforce PII redaction, topic denial, and contextual grounding checks",
            "B. Guardrails replace VPC networking and Knowledge Bases compile C++ kernels",
            "C. Both services only store static DNS `A` records",
            "D. Knowledge Bases disable TLS encryption to speed up token streaming"
        ],
        "correct_answer": "A",
        "explanation": "Amazon Bedrock Knowledge Bases automate chunking, embeddings, and vector search for grounded RAG, while Bedrock Guardrails filter harmful content, PII, and hallucinations."
    },
    {
        "topic": "Web Development & Cloud", "difficulty": "Hard",
        "question": "In `Amazon DynamoDB`, what causes a **hot partition** bottleneck under heavy traffic, and how is it mitigated?",
        "options": [
            "A. Low-cardinality partition keys funnel disproportionate `RCU`/`WCU` onto one physical shard; mitigate with high-cardinality composite keys or write sharding suffixes",
            "B. Using `JOIN` clauses across normalized 5NF foreign-key tables",
            "C. Running `VACUUM FULL` locks on DynamoDB every minute",
            "D. Choosing `UTF-8` strings shorter than 64 characters"
        ],
        "correct_answer": "A",
        "explanation": "DynamoDB hashes the Partition Key to distribute items across storage partitions; high-cardinality keys (e.g., `tenant_id#user_id` or random shard suffixes) spread throughput evenly."
    },
]


def seed():
    from database.db_manager import save_questions_to_bank, init_db
    init_db()
    save_questions_to_bank(CURRICULUM_DATASET)
    print(f"Successfully seeded {len(CURRICULUM_DATASET)} curated questions into questions_bank.")


if __name__ == "__main__":
    seed()
