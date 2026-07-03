#!/usr/bin/env python3
"""
Markov Chain Captain's Log Generator

Implements a configurable-order Markov chain text generator trained on
Star Trek captain's log entries. No ML libraries — pure probability.

Author: Ensign Wesley
Stardate: 2026-02-16
"""

import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple

class MarkovChain:
    """
    Markov chain text generator with configurable order.
    
    Order 1 (bigram): P(word_n | word_n-1)
    Order 2 (trigram): P(word_n | word_n-2, word_n-1)
    Order N: P(word_n | word_n-N, ..., word_n-1)
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize Markov chain.
        
        Args:
            order: N-gram order (1=bigram, 2=trigram, etc.)
        """
        self.order = order
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.starts: List[Tuple[str, ...]] = []
    
    def train(self, texts: List[str]):
        """
        Train the Markov chain on a corpus of texts.
        
        Args:
            texts: List of training texts
        """
        for text in texts:
            tokens = self._tokenize(text)
            
            if len(tokens) < self.order + 1:
                continue
            
            # Store starting n-gram
            start = tuple(tokens[:self.order])
            self.starts.append(start)
            
            # Build transition table
            for i in range(len(tokens) - self.order):
                state = tuple(tokens[i:i + self.order])
                next_word = tokens[i + self.order]
                self.chain[state].append(next_word)
    
    def generate(self, max_length: int = 100, min_length: int = 30) -> str:
        """
        Generate text using the Markov chain.
        
        Args:
            max_length: Maximum number of words
            min_length: Minimum number of words
        
        Returns:
            Generated text
        """
        if not self.starts:
            return "Error: Chain not trained"
        
        # Start with a random starting n-gram
        current = list(random.choice(self.starts))
        output = list(current)
        
        # Generate until we hit max length or a natural ending
        for _ in range(max_length - self.order):
            state = tuple(current[-self.order:])
            
            # Get possible next words
            if state not in self.chain:
                break
            
            next_words = self.chain[state]
            next_word = random.choice(next_words)
            output.append(next_word)
            current.append(next_word)
            
            # Stop at sentence end if we're past min length
            if len(output) >= min_length and next_word.endswith('.'):
                break
        
        return self._finish_sentence(output, min_length)

    def _finish_sentence(self, tokens: List[str], min_length: int) -> str:
        """
        Return generated tokens as a clean sentence.

        Markov walks can hit ``max_length`` in the middle of a thought. Prefer a
        natural sentence boundary once the requested minimum length is met; if
        none exists, lightly normalize the fragment so the browser/CLI output
        still reads like a captain's log rather than a raw token stream.
        """
        if not tokens:
            return ""

        for i in range(len(tokens) - 1, min_length - 2, -1):
            if tokens[i].endswith(('.', '!', '?')):
                tokens = tokens[:i + 1]
                break

        text = ' '.join(tokens).strip()
        if not text:
            return text

        text = text[0].upper() + text[1:]
        if not text.endswith(('.', '!', '?')):
            text += '.'
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words, preserving punctuation.
        
        Args:
            text: Input text
        
        Returns:
            List of tokens
        """
        # Split on whitespace but keep punctuation attached to words
        tokens = text.split()
        return tokens
    
    def stats(self) -> Dict:
        """Get statistics about the trained chain"""
        total_transitions = sum(len(v) for v in self.chain.values())
        unique_states = len(self.chain)
        
        return {
            'order': self.order,
            'unique_states': unique_states,
            'total_transitions': total_transitions,
            'starting_states': len(self.starts),
            'avg_transitions_per_state': total_transitions / unique_states if unique_states > 0 else 0
        }


def load_logs(filename: str) -> List[str]:
    """Load captain's logs from file"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split on double newlines (log separator)
    logs = [log.strip() for log in content.split('\n\n') if log.strip()]
    return logs


def main():
    """Main execution"""
    print("=== MARKOV CHAIN CAPTAIN'S LOG GENERATOR ===")
    print("Ensign Wesley • Stardate 2026-02-16\n")
    
    # Load training data
    print("Loading captain's logs...")
    logs = load_logs('captains_logs_raw.txt')
    print(f"Loaded {len(logs)} log entries\n")
    
    # Train models with different orders
    orders_to_test = [1, 2, 3]
    models = {}
    
    for order in orders_to_test:
        print(f"Training order-{order} model ({['bigram', 'trigram', '4-gram'][order-1]})...")
        model = MarkovChain(order=order)
        model.train(logs)
        models[order] = model
        
        stats = model.stats()
        print(f"  States: {stats['unique_states']}, Transitions: {stats['total_transitions']}")
        print(f"  Avg transitions/state: {stats['avg_transitions_per_state']:.2f}\n")
    
    # Generate logs with each model
    print("="*60)
    print("GENERATED CAPTAIN'S LOGS")
    print("="*60)
    
    for order in orders_to_test:
        print(f"\n--- ORDER {order} ({['BIGRAM', 'TRIGRAM', '4-GRAM'][order-1]}) ---\n")
        
        for i in range(3):
            log = models[order].generate(max_length=80, min_length=30)
            print(f"Log {i+1}:")
            print(log)
            print()
    
    # Generate final batch with best model (order 2)
    print("="*60)
    print("FINAL SELECTION (Trigram Model)")
    print("="*60)
    
    best_model = models[2]
    final_logs = []
    
    for i in range(5):
        log = best_model.generate(max_length=100, min_length=40)
        final_logs.append(log)
        print(f"\n--- FINAL LOG {i+1} ---")
        print(log)
    
    # Save the best logs
    with open('generated_logs.txt', 'w') as f:
        for i, log in enumerate(final_logs):
            f.write(f"=== Generated Log {i+1} ===\n")
            f.write(log + "\n\n")
    
    print("\n" + "="*60)
    print("Generated logs saved to generated_logs.txt")
    print("="*60)


if __name__ == "__main__":
    main()
