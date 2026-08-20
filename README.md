# eos-core

_Type-checked, dependency-free utility library for modern Python_

[![PyPI Version](https://img.shields.io/pypi/v/info.gianlucacosta.eos-core?style=for-the-badge&logo=python&logoColor=white&color=forestgreen)](https://pypi.org/project/info.gianlucacosta.eos-core/)

## Introduction

My voyage through the vast and fascinating universe of **Python** started back in 2004 - when _Python 2.3_ was still the latest, exciting release... 😊

Since then, both the language and its ecosystem have evolved a lot: in particular, I feel that _type hints_ make Python even more robust, without sacrificing its charming syntax - just like another language I'm fond of: **TypeScript**.

Consequently, the **Eos** library is designed to provide a set of shared utilities and patterns emerged during the creation of my open source projects with modern, type-checked Python - and this **core** package only builds upon the standard library, with no additional runtime dependencies.

For further details, please refer to the sections below, to the documentation within each module, and even to the tests - whose coverage is more than 97%! ^\_\_^

## Installation

To install **eos.core**, just run:

> pip install info.gianlucacosta.eos.core

or, if you prefer using Poetry:

> poetry add info.gianlucacosta.eos.core

Then, you'll be able to access the **info.gianlucacosta.eos.core** package and its subpackages.

## Highlights

**eos.core** provides a wide variety of patterns - including:

- _higher-order functional abstractions_, such as functions returning **adaptable queue writers** and **readers** - whose timeouts vary according to the queue state

- a disposable **TemporaryPath** - and a **Uuid4TemporaryPath** string subclass that perform advanced cleanup, no matter whether you create a file or a whole directory tree upon it

- a **BufferedDbSerializer** - using advanced but simple decorators to serialize objects of different types via dedicated SQL statements, but actually writing to DB only when the internal buffer is full

- an **InThreadPool** class having the same interface as Python's **Pool** - but running within the very same thread: definitely handful when debugging and testing

- a **CancelableThread** and the related **CancelableThreadHandle** - enabling the client to send a cancelation request

- an **Atomic** class, to read and update arbitrary values atomically

- a **functional** module, with expressive type aliases for functions - with ideas borrowed from other languages such as C#, Java and Rust

...and more! ^\_\_^ It's definitely not easy to mention everything in a README file, so please feel free to browse the modules and explore how they are used in the tests!
