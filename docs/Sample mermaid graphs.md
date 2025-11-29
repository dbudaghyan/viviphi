### 1\. The "Kitchen Sink" Flowchart

This graph tests node shapes, edge types, label formatting, and directionality. It is excellent for testing parsing logic and rendering capabilities.

```mermaid
graph TD
    %% Basic Shapes and Edges
    A[Rectangular Node] -->|Text on Edge| B(Round Edge)
    B --> C{Decision Diamond}
    C -->|One| D[Result One]
    C -->|Two| E[Result Two]

    %% Complex Edges
    E -.->|Dotted| F((Circle))
    F ==>|Thick| G([Stadium])
    G --o|Circle Edge| H[[Subroutine]]
    H x-x|Cross Edge| I[(Database)]

    %% Trapped Shapes & Odd Characters
    J>Asymmetric] --> K{{Hexagon}}
    K --> L[/Parallelogram/]
    L --> M[\Trapezoid alt\]
```

-----

### 2\. Nested Subgraphs & Direction

Use this to test recursive parsing, scope handling, and how your library handles clusters.

```mermaid
flowchart LR
    subgraph TOP_LEVEL [Top Level Group]
        direction TB
        subgraph NESTED_A [Nested Cluster A]
            direction RL
            A1(Start A) --> A2(End A)
        end
        subgraph NESTED_B [Nested Cluster B]
            B1{Check B} --> B2[Process B]
        end
        NESTED_A --> NESTED_B
    end
    OutsideNode --> TOP_LEVEL
```

-----

### 3\. Styling and Classes (CSS/Theme Testing)

If your library modifies, extracts, or renders styles, this string tests `classDef`, inline styles, and class attachment.

```mermaid
graph TD
    A:::someClass --> B
    B("Styled Inline"):::otherClass
    C[Normal Node] --> D[Error Node]

    %% Styles
    style B fill:#f9f,stroke:#333,stroke-width:4px
    style D fill:#bbf,stroke:#f66,stroke-width:2px,color:#fff,stroke-dasharray: 5 5

    %% Class Definitions
    classDef someClass fill:#f96,stroke:#333,stroke-width:2px;
    classDef otherClass fill:#bbf,stroke:#333,stroke-width:2px;
    classDef errorClass fill:#f00,color:white;

    class D errorClass;
```

-----

### 4\. Special Characters, Escaping, and Unicode

This is crucial for testing encoding errors, JSON serialization issues, or parser crashes due to symbols.

```mermaid
graph TD
    A["Node with spaces"] --> B["Node with \"quotes\" inside"]
    B --> C["Unicode: 🚀 ❤️ α, β, γ"]
    C --> D["Special chars: ! @ # $ % ^ & * ( ) _ + - = [ ] { } | ; : , . < > ?"]
    D --> E["<b>HTML Bold</b> and <i>Italic</i>"]
    E --> F["Markdown **Bold** and *Italic*"]
```

-----

### 5\. Sequence Diagram

Sequence diagrams use a completely different syntax grammar (using `->>` vs `-->`). This tests if your library supports non-flowchart parsing.

```mermaid
sequenceDiagram
    autonumber
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
    alt is sick
        Bob->>Alice: Not so good
    else is well
        Bob->>Alice: Feeling fresh
    end
```

-----

### 6\. Class Diagram (Object Oriented)

Tests cardinality, visibility identifiers (`+`, `-`, `#`), and type relationships.

```mermaid
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
    class Fish{
        -int sizeInFeet
        -canEat()
    }
```

-----

### 7\. State Diagram (v2)

Tests composite states and transition logic.

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
    
    state Moving {
        [*] --> Accelerating
        Accelerating --> Decelerating
        Decelerating --> Accelerating
    }
```

-----

### 8\. Entity Relationship Diagram (ER)

Tests distinct connector syntax (one-to-one, one-to-many).

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
    ORDER {
        int order_id
        string delivery_address
    }
```

-----

### 9\. Gantt Chart

Tests date parsing, axis formatting, and exclusion logic.

```mermaid
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1  , 20d
    section Another
    Task in sec      :2014-01-12  , 12d
    another task      : 24d
```

-----

### 10\. Large Data / Stress Test

A programmed structure to test memory handling or rendering timeouts.

```mermaid
graph TD
    A1-->A2; A2-->A3; A3-->A4; A4-->A5; A5-->A1;
    B1-->B2; B2-->B3; B3-->B4; B4-->B5; B5-->B1;
    C1-->C2; C2-->C3; C3-->C4; C4-->C5; C5-->C1;
    A1-->B1; B1-->C1; C1-->A1;
    A3-->B3; B3-->C3;
```

### 11\. Broken / Invalid Syntax

(Optional but recommended) Feed this to your library to ensure it fails gracefully (raises a specific error rather than crashing).

```mermaid
graph TD
    A --> B
    C -..- // Missing node or bad syntax
    subgraph MISSING_END
    D --> E
```

### 12\. Interaction (Click Events)

If your library handles interactivity or web embedding, test the `click` binding.

```mermaid
graph LR
    A[Clickable Node] --> B
    click A "https://www.github.com" "Tooltip text"
    click B callbackFunction "Javascript Callback"
```

-----
