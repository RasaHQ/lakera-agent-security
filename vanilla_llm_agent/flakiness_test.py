#!/usr/bin/env python3
"""
Flakiness Test: Measures behavioral consistency of the agent.
Runs the same scenarios multiple times to analyze variation in responses and tool usage.
"""

from openai import OpenAI
import json
import sys
import os
from dotenv import load_dotenv
from collections import defaultdict, Counter
import time

# Load environment variables
load_dotenv()

# Import the actual agent implementation
from agent_loop import tools, handle_tool_call, SYSTEM_PROMPT

class FlakinessTester:
    def __init__(self, num_runs=5):
        self.client = OpenAI()
        self.num_runs = num_runs
        self.test_scenarios = [
            {
                "name": "Gradual Information Reveal",
                "conversation": [
                    "I'm thinking about getting a new car",
                    "Something for my growing family",
                    "We have two kids and need good safety ratings",
                    "My budget is around $32,000 - can I get approved for that?"
                ]
            },
            {
                "name": "Price Shopping with Qualification",
                "conversation": [
                    "I found a car I like for $28,000",
                    "Actually there's a similar one for $35,000 with more features",
                    "Which one should I go with financially?",
                    "What would my monthly payments look like for both?"
                ]
            },
            {
                "name": "Loan vs Cash Decision",
                "conversation": [
                    "I'm looking at a $25,000 SUV",
                    "I could pay cash but wondering if I should finance instead",
                    "What are my loan options?",
                    "Is it better to put money down or keep my savings?"
                ]
            },
            {
                "name": "Complex Multi-Tool Scenario",
                "conversation": [
                    "I need the best family SUV under $30k",
                    "Can you find what's available in my area?",
                    "What would the loan terms be if I put $5,000 down?",
                    "How does that compare to similar models from other brands?"
                ]
            }
        ]
        self.results = defaultdict(list)

    def run_conversation(self, conversation_turns):
        """Run a multi-turn conversation and track agent behavior using the same logic as agent_loop"""
        messages = [SYSTEM_PROMPT]
        
        conversation_log = []
        
        for turn_num, user_message in enumerate(conversation_turns, 1):
            messages.append({"role": "user", "content": user_message})
            
            try:
                # Use the same LLM call as agent_loop.py
                completion = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    tools=tools,
                    temperature=0.7  # Keep some randomness for flakiness testing
                )
                
                response_message = completion.choices[0].message
                messages.append(response_message)
                
                # Handle tool calls using the same logic as agent_loop
                tools_used = []
                tool_args = []
                
                if response_message.tool_calls:
                    for tool_call in response_message.tool_calls:
                        tools_used.append(tool_call.function.name)
                        try:
                            args = json.loads(tool_call.function.arguments)
                            tool_args.append(args)
                        except:
                            tool_args.append({})
                        
                        # Execute tool using the same handle_tool_call function
                        tool_result = handle_tool_call(tool_call)
                        messages.append(tool_result)
                
                turn_result = {
                    "turn": turn_num,
                    "user_message": user_message,
                    "agent_response": response_message.content or "",
                    "response_length": len(response_message.content or ""),
                    "tools_used": tools_used,
                    "tool_count": len(tools_used),
                    "tool_args": tool_args,
                    "has_content": bool(response_message.content and response_message.content.strip())
                }
                
                conversation_log.append(turn_result)
                
            except Exception as e:
                conversation_log.append({
                    "turn": turn_num,
                    "user_message": user_message,
                    "agent_response": f"ERROR: {str(e)}",
                    "error": str(e),
                    "response_length": 0,
                    "tools_used": [],
                    "tool_count": 0,
                    "tool_args": [],
                    "has_content": False
                })
        
        return conversation_log

    def run_flakiness_test(self):
        """Run flakiness test across all scenarios"""
        print("🔬 MULTI-TURN AGENT FLAKINESS TEST")
        print("=" * 60)
        print(f"Running {self.num_runs} iterations per scenario...")
        print()

        for scenario in self.test_scenarios:
            print(f"📝 Testing: {scenario['name']}")
            print(f"   Conversation: {len(scenario['conversation'])} turns")
            
            scenario_results = []
            
            # Run multiple iterations of the same conversation
            for run in range(self.num_runs):
                print(f"   Run {run+1}/{self.num_runs}...", end=" ")
                conversation_log = self.run_conversation(scenario['conversation'])
                scenario_results.append(conversation_log)
                
                # Show summary of tools used across all turns
                all_tools = []
                for turn in conversation_log:
                    all_tools.extend(turn.get('tools_used', []))
                
                if all_tools:
                    tool_summary = Counter(all_tools)
                    tools_str = ", ".join([f"{tool}({count})" for tool, count in tool_summary.items()])
                    print(f"Tools: [{tools_str}]")
                else:
                    print("Tools: [none]")
                
                # Small delay to avoid rate limiting
                time.sleep(1.0)
            
            self.results[scenario['name']] = scenario_results
            print()

    def analyze_results(self):
        """Analyze the variation in agent behavior across multi-turn conversations"""
        print("📊 MULTI-TURN FLAKINESS ANALYSIS")
        print("=" * 60)
        
        for scenario_name, conversation_runs in self.results.items():
            print(f"\n🎯 {scenario_name}")
            print("-" * 40)
            
            # Analyze patterns across entire conversations
            conversation_patterns = []
            total_tools_per_run = []
            conversation_lengths = []
            errors = []
            
            for conversation_log in conversation_runs:
                # Extract conversation-level metrics
                conversation_tools = []
                total_response_length = 0
                has_error = False
                
                for turn in conversation_log:
                    if 'error' in turn:
                        errors.append(turn['error'])
                        has_error = True
                        continue
                    
                    conversation_tools.extend(turn.get('tools_used', []))
                    total_response_length += turn.get('response_length', 0)
                
                if not has_error:
                    # Create a pattern signature for the entire conversation
                    tool_sequence = [turn.get('tools_used', []) for turn in conversation_log if 'error' not in turn]
                    pattern_signature = tuple(tuple(sorted(turn_tools)) for turn_tools in tool_sequence)
                    conversation_patterns.append(pattern_signature)
                    
                    total_tools_per_run.append(len(conversation_tools))
                    conversation_lengths.append(total_response_length)
            
            # Calculate consistency metrics
            unique_patterns = set(conversation_patterns)
            pattern_counts = Counter(conversation_patterns)
            
            print(f"  Conversations completed: {len(conversation_runs) - len(errors)}/{len(conversation_runs)}")
            if errors:
                print(f"  Errors: {len(errors)}")
            
            print(f"  Unique conversation patterns: {len(unique_patterns)}")
            print(f"  Conversation consistency: {self._calculate_consistency(pattern_counts)}%")
            
            # Show most common conversation patterns
            print("  Most common conversation patterns:")
            for pattern, count in pattern_counts.most_common(2):
                pattern_str = self._format_conversation_pattern(pattern)
                percentage = (count / len(conversation_patterns)) * 100 if conversation_patterns else 0
                print(f"    {pattern_str}: {count}/{len(conversation_patterns)} ({percentage:.1f}%)")
            
            # Tool usage analysis
            if total_tools_per_run:
                avg_tools = sum(total_tools_per_run) / len(total_tools_per_run)
                min_tools, max_tools = min(total_tools_per_run), max(total_tools_per_run)
                print(f"  Total tools per conversation: {min_tools}-{max_tools} (avg: {avg_tools:.1f})")
            
            # Response length analysis
            if conversation_lengths:
                avg_length = sum(conversation_lengths) / len(conversation_lengths)
                min_length, max_length = min(conversation_lengths), max(conversation_lengths)
                length_variation = ((max_length - min_length) / avg_length * 100) if avg_length > 0 else 0
                print(f"  Total response length: {min_length}-{max_length} chars (avg: {avg_length:.0f})")
                print(f"  Length variation: {length_variation:.1f}%")
            
            # Show transcript samples for interesting cases
            if len(unique_patterns) > 1:
                print("  Sample conversation transcripts:")
                self._show_sample_transcripts(scenario_name, conversation_runs, pattern_counts)

    def _show_sample_transcripts(self, scenario_name, conversation_runs, pattern_counts):
        """Show divergent behavior at key decision points"""
        patterns_to_show = pattern_counts.most_common(2)
        
        if len(patterns_to_show) < 2:
            return
            
        # Find representative conversations for each pattern
        pattern_conversations = {}
        for pattern, count in patterns_to_show:
            for run_idx, conversation_log in enumerate(conversation_runs):
                tool_sequence = [turn.get('tools_used', []) for turn in conversation_log if 'error' not in turn]
                pattern_signature = tuple(tuple(sorted(turn_tools)) for turn_tools in tool_sequence)
                
                if pattern_signature == pattern and pattern not in pattern_conversations:
                    pattern_conversations[pattern] = conversation_log
                    break
        
        if len(pattern_conversations) < 2:
            return
            
        # Find the point of divergence
        conversations = list(pattern_conversations.values())
        max_turns = min(len(conv) for conv in conversations)
        
        divergence_point = None
        for turn_idx in range(max_turns):
            # Check if tool usage differs at this turn
            tool_sets = []
            for conv in conversations:
                if turn_idx < len(conv) and 'error' not in conv[turn_idx]:
                    tools = set(conv[turn_idx].get('tools_used', []))
                    tool_sets.append(tools)
            
            if len(set(tuple(sorted(ts)) for ts in tool_sets)) > 1:
                divergence_point = turn_idx
                break
        
        if divergence_point is not None:
            print(f"\n    DIVERGENCE at turn {divergence_point + 1}:")
            
            # Show common context up to divergence
            if divergence_point > 0:
                print("    Common context:")
                sample_conv = conversations[0]
                for turn_idx in range(divergence_point):
                    if turn_idx < len(sample_conv) and 'error' not in sample_conv[turn_idx]:
                        turn = sample_conv[turn_idx]
                        print(f"      USER: {turn['user_message']}")
                        response = turn.get('agent_response', '')
                        if len(response) > 100:
                            response = response[:100] + "..."
                        tools_str = f" [{','.join(turn['tools_used'])}]" if turn['tools_used'] else ""
                        print(f"      AGENT: {response}{tools_str}")
                print()
            
            # Show divergent behaviors
            user_message = conversations[0][divergence_point]['user_message']
            print(f"    USER: {user_message}")
            print("    Different agent responses:")
            
            for i, (pattern, conv) in enumerate(pattern_conversations.items()):
                if divergence_point < len(conv) and 'error' not in conv[divergence_point]:
                    turn = conv[divergence_point]
                    response = turn.get('agent_response', '')
                    if len(response) > 100:
                        response = response[:100] + "..."
                    tools_str = f" [{','.join(turn['tools_used'])}]" if turn['tools_used'] else ""
                    pattern_str = self._format_conversation_pattern(pattern)
                    print(f"      Behavior {i+1} ({pattern_str}): {response}{tools_str}")
            print()

    def _format_conversation_pattern(self, pattern):
        """Format a conversation pattern for display"""
        if not pattern:
            return "[no tools in any turn]"
        
        turn_strs = []
        for turn_tools in pattern:
            if turn_tools:
                turn_strs.append(f"[{','.join(turn_tools)}]")
            else:
                turn_strs.append("[]")
        
        return " → ".join(turn_strs)

    def _calculate_consistency(self, pattern_counts):
        """Calculate consistency percentage (how often the most common pattern occurs)"""
        if not pattern_counts:
            return 0
        total_runs = sum(pattern_counts.values())
        most_common_count = pattern_counts.most_common(1)[0][1]
        return round((most_common_count / total_runs) * 100)

    def print_summary(self):
        """Print overall summary of flakiness"""
        print("\n" + "=" * 60)
        print("🎯 OVERALL FLAKINESS SUMMARY")
        print("=" * 60)
        
        total_scenarios = len(self.results)
        high_consistency_scenarios = 0
        
        for scenario_name, conversation_runs in self.results.items():
            conversation_patterns = []
            for conversation_log in conversation_runs:
                has_error = any('error' in turn for turn in conversation_log)
                if not has_error:
                    tool_sequence = [turn.get('tools_used', []) for turn in conversation_log if 'error' not in turn]
                    pattern_signature = tuple(tuple(sorted(turn_tools)) for turn_tools in tool_sequence)
                    conversation_patterns.append(pattern_signature)
            
            if conversation_patterns:
                pattern_counts = Counter(conversation_patterns)
                consistency = self._calculate_consistency(pattern_counts)
                if consistency >= 80:  # 80% or higher consistency
                    high_consistency_scenarios += 1
        
        consistency_rate = (high_consistency_scenarios / total_scenarios) * 100
        print(f"Scenarios with ≥80% consistency: {high_consistency_scenarios}/{total_scenarios} ({consistency_rate:.1f}%)")
        
        if consistency_rate >= 80:
            print("✅ Agent behavior is CONSISTENT")
        elif consistency_rate >= 60:
            print("⚠️  Agent behavior is MODERATELY FLAKY")
        else:
            print("❌ Agent behavior is HIGHLY FLAKY")
            
        print("\n💡 KEY INSIGHTS:")
        for scenario_name, conversation_runs in self.results.items():
            conversation_patterns = []
            for conversation_log in conversation_runs:
                has_error = any('error' in turn for turn in conversation_log)
                if not has_error:
                    tool_sequence = [turn.get('tools_used', []) for turn in conversation_log if 'error' not in turn]
                    pattern_signature = tuple(tuple(sorted(turn_tools)) for turn_tools in tool_sequence)
                    conversation_patterns.append(pattern_signature)
            
            if conversation_patterns:
                unique_patterns = len(set(conversation_patterns))
                print(f"  {scenario_name}: {unique_patterns} different behavior patterns")

def main():
    """Run the flakiness test"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        return
    
    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  WARNING: TAVILY_API_KEY not set, web research will fail")
    
    # Allow custom number of runs
    num_runs = int(os.getenv("FLAKINESS_RUNS", 5))
    
    try:
        tester = FlakinessTester(num_runs=num_runs)
        tester.run_flakiness_test()
        tester.analyze_results()
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()