"""
Batch Processor for Declare-SBMN Mining
Processes multiple .xes files from a folder structure and tracks processing time.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict
from Declare4Py.ProcessMiningTasks.Discovery.DeclareMiner import DeclareMiner
from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessModels.DeclareModel import DeclareModel
from declaresbmn_layered import sbmn_mining
from sbmn_model_functions import parse_sbmn_model, generate_json_from_sbmn
from assertiontests_functions import SBMNValidator, Situation, Operator
from confirmation_functions import accuracy_tracker
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.alpha import algorithm as alpha_miner


class SituationEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Situation objects and other non-serializable types."""
    
    def default(self, obj):
        if isinstance(obj, Situation):
            return {
                "esquerda": obj.left,
                "direita": obj.right,
                "operador": obj.op.value
            }
        elif isinstance(obj, Operator):
            return obj.value
        return super().default(obj)


class BatchProcessor:
    """Process multiple .xes files and track processing time."""
    
    def __init__(self, main_folder, output_folder="OUTPUTS", 
                 min_support_layer1=0.6, min_support_layer2=0.1,
                 itemsets_support_layer1=0.01, itemsets_support_layer2=0.00001):
        """
        Initialize batch processor.
        
        Args:
            main_folder: Main folder containing subfolders with .xes files
            output_folder: Folder to save outputs
            min_support_layer1: Minimum support for first layer mining
            min_support_layer2: Minimum support for second layer mining
            itemsets_support_layer1: Itemsets support for first layer
            itemsets_support_layer2: Itemsets support for second layer
        """
        self.main_folder = Path(main_folder)
        self.output_folder = Path(output_folder)
        self.min_support_layer1 = min_support_layer1
        self.min_support_layer2 = min_support_layer2
        self.itemsets_support_layer1 = itemsets_support_layer1
        self.itemsets_support_layer2 = itemsets_support_layer2
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(exist_ok=True)
        
        # Initialize results tracking
        self.processing_results = []
        
    def find_xes_files(self):
        """
        Find all .xes files in the main folder and subfolders.
        
        Returns:
            List of tuples (file_path, relative_path)
        """
        xes_files = []
        for root, dirs, files in os.walk(self.main_folder):
            for file in files:
                if file.endswith('.xes'):
                    full_path = Path(root) / file
                    relative_path = full_path.relative_to(self.main_folder)
                    xes_files.append((full_path, relative_path))
        
        return xes_files
    
    def process_single_file(self, file_path, relative_path):
        """
        Process a single .xes file and track processing time.
        
        Args:
            file_path: Path to the .xes file
            relative_path: Relative path from main folder
            
        Returns:
            Dictionary with processing results
        """
        print(f"\n{'='*80}")
        print(f"Processing: {relative_path}")
        print(f"{'='*80}")
        
        result = {
            'file_path': str(file_path),
            'relative_path': str(relative_path),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'times': {}
        }
        
        try:
            # Start total time
            total_start = time.time()
            
            # Load event log
            print("\n[1/5] Loading event log...")
            load_start = time.time()
            event_log = D4PyEventLog(case_name="case:concept:name")
            event_log.parse_xes_log(str(file_path))
            load_time = time.time() - load_start
            result['times']['load_log'] = load_time
            print(f"   Loaded in {load_time:.2f}s")
            
            # First layer mining
            print("\n[2/5] Mining constraints - First Layer...")
            layer1_start = time.time()
            discovery_1 = DeclareMiner(
                log=event_log,
                consider_vacuity=False,
                min_support=self.min_support_layer1,
                itemsets_support=self.itemsets_support_layer1,
                max_declare_cardinality=3
            )
            discovered_model_first_layer: DeclareModel = discovery_1.run()
            layer1_time = time.time() - layer1_start
            result['times']['layer1_mining'] = layer1_time
            result['layer1_constraints_count'] = len(discovered_model_first_layer.serialized_constraints)
            print(f"   First layer mining completed in {layer1_time:.2f}s")
            # print(f"   Extracted {len(discovered_model_first_layer.serialized_constraints)} constraints")
            
            # SBMN mining (includes second layer)
            print("\n[3/5] SBMN Mining (Second Layer)...")
            sbmn_start = time.time()
            matrix, sbmn, accuracy_summary = sbmn_mining(discovered_model_first_layer.serialized_constraints, event_log)
            sbmn_time = time.time() - sbmn_start
            result['times']['sbmn_mining'] = sbmn_time
            result['sbmn_model_size'] = len(sbmn)
            result['heuristic_accuracy'] = accuracy_summary
            print(f"   SBMN mining completed in {sbmn_time:.2f}s")
            # print(f"   Generated {len(sbmn)} SBMN elements")
            
            # Inductive Miner
            print("\n[3.5/5] Running Inductive Miner...")
            inductive_start = time.time()
            try:
                inductive_tree = inductive_miner.apply(event_log.log)
                inductive_time = time.time() - inductive_start
                result['times']['inductive_miner'] = inductive_time
                print(f"   Inductive Miner completed in {inductive_time:.2f}s")
            except Exception as e:
                result['times']['inductive_miner'] = 0
                print(f"   Inductive Miner failed: {str(e)}")
            
            # Alpha Miner
            print("\n[3.7/5] Running Alpha Miner...")
            alpha_start = time.time()
            try:
                alpha_net, alpha_initial_marking, alpha_final_marking = alpha_miner.apply(
                    event_log.log, 
                    variant=alpha_miner.Variants.ALPHA_VERSION_PLUS
                )
                alpha_time = time.time() - alpha_start
                result['times']['alpha_miner'] = alpha_time
                print(f"   Alpha Miner completed in {alpha_time:.2f}s")
            except Exception as e:
                result['times']['alpha_miner'] = 0
                print(f"   Alpha Miner failed: {str(e)}")
            
            # Validate model
            print("\n[4/5] Validating SBMN model...")
            validation_start = time.time()
            sbmn_model = parse_sbmn_model(sbmn)
            validator = SBMNValidator()
            validation_result = validator.validate_model(sbmn_model)
            validation_time = time.time() - validation_start
            result['times']['validation'] = validation_time
            result['validation_result'] = validation_result
            print(f"   Validation completed in {validation_time:.2f}s")
            
            # Generate JSON output
            print("\n[5/5] Generating JSON output...")
            json_start = time.time()
            
            # Create subfolder structure in output
            output_subfolder = self.output_folder / relative_path.parent
            output_subfolder.mkdir(parents=True, exist_ok=True)
            
            # Generate file name
            log_name = file_path.stem  # filename without extension
            output_json_path = output_subfolder / f"sbmn_{log_name}.json"
            
            # Generate JSON
            json_model = generate_json_from_sbmn(matrix, {}, str(output_json_path))
            json_time = time.time() - json_start
            result['times']['json_generation'] = json_time
            result['output_json'] = str(output_json_path)
            print(f"   JSON generated in {json_time:.2f}s")
            print(f"   Saved to: {output_json_path}")
            
            # Calculate total time
            total_time = time.time() - total_start
            result['times']['total'] = total_time
            result['success'] = True
            
            print(f"\n COMPLETED in {total_time:.2f}s")
            
        except Exception as e:
            result['error'] = str(e)
            result['times']['total'] = time.time() - total_start
            print(f"\n ERROR: {e}")
        
        return result
    
    def process_all_files(self):
        """
        Process all .xes files found in the main folder structure.
        
        Returns:
            Summary statistics
        """
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING STARTED")
        print(f"{'='*80}")
        print(f"Main folder: {self.main_folder}")
        print(f"Output folder: {self.output_folder}")
        
        # Find all .xes files
        xes_files = self.find_xes_files()
        print(f"\nFound {len(xes_files)} .xes file(s)")
        
        if not xes_files:
            print("\n No .xes files found!")
            return None
        
        # Process each file
        batch_start = time.time()
        
        for i, (file_path, relative_path) in enumerate(xes_files, 1):
            print(f"\n\n[File {i}/{len(xes_files)}]")
            result = self.process_single_file(file_path, relative_path)
            self.processing_results.append(result)
        
        batch_total_time = time.time() - batch_start
        
        # Generate summary
        summary = self.generate_summary(batch_total_time)
        
        # Save results to JSON
        self.save_results(summary)
        
        # Generate performance graphs
        self.generate_performance_graphs(summary)
        
        # Generate text reports
        self.generate_performance_report_table(summary)
        self.generate_validation_report_table(summary)
        self.generate_combined_report(summary)
        
        # Generate folder statistics report
        self.generate_folder_statistics_report(summary)
        
        return summary
    
    def generate_summary(self, batch_total_time):
        """Generate processing summary statistics."""
        successful = [r for r in self.processing_results if r['success']]
        failed = [r for r in self.processing_results if not r['success']]
        
        summary = {
            'batch_info': {
                'main_folder': str(self.main_folder),
                'output_folder': str(self.output_folder),
                'timestamp': datetime.now().isoformat(),
                'total_files': len(self.processing_results),
                'successful': len(successful),
                'failed': len(failed),
                'batch_total_time': batch_total_time
            },
            'mining_parameters': {
                'min_support_layer1': self.min_support_layer1,
                'min_support_layer2': self.min_support_layer2,
                'itemsets_support_layer1': self.itemsets_support_layer1,
                'itemsets_support_layer2': self.itemsets_support_layer2
            },
            'time_statistics': {},
            'detailed_results': self.processing_results
        }
        
        # Calculate time statistics for successful runs
        if successful:
            time_keys = ['load_log', 'layer1_mining', 'sbmn_mining', 'validation', 'json_generation', 'total']
            for key in time_keys:
                times = [r['times'].get(key, 0) for r in successful if key in r['times']]
                if times:
                    summary['time_statistics'][key] = {
                        'min': min(times),
                        'max': max(times),
                        'avg': sum(times) / len(times),
                        'total': sum(times)
                    }
        
        return summary
    
    def _serialize_situation(self, situation):
        """Convert Situation object to JSON-serializable dictionary (in Portuguese)."""
        if isinstance(situation, Situation):
            return {
                "esquerda": situation.left,
                "direita": situation.right,
                "operador": situation.op.value
            }
        return str(situation)
    
    def _serialize_heuristic_accuracy(self, accuracy_data):
        """Convert heuristic accuracy data to JSON-serializable format (in Portuguese)."""
        if isinstance(accuracy_data, dict):
            serialized = {}
            for key, value in accuracy_data.items():
                if isinstance(value, dict):
                    serialized[key] = {
                        "acertos": value.get('acertos', 0),
                        "erros": value.get('erros', 0),
                        "total": value.get('total', 0),
                        "taxa_acerto": round(value.get('taxa_acerto', 0), 2)
                    }
                else:
                    serialized[key] = value
            return serialized
        return accuracy_data
    
    def _serialize_validation_result(self, validation_result):
        """Convert validation result to JSON-serializable format (in Portuguese)."""
        if not validation_result:
            return validation_result
        
        if isinstance(validation_result, dict):
            serialized = {}
            for key, value in validation_result.items():
                # Traduzir chaves para português
                key_traduzido = {
                    'valid': 'valido',
                    'accepted': 'aceitas',
                    'errors': 'erros',
                    'dep_graph': 'grafo_dependencias',
                    'situation': 'situacao',
                    'reason': 'motivo'
                }.get(key, key)
                
                if isinstance(value, list):
                    # Se for lista, serializa cada elemento
                    serialized[key_traduzido] = []
                    for item in value:
                        if isinstance(item, Situation):
                            serialized[key_traduzido].append(self._serialize_situation(item))
                        elif isinstance(item, dict):
                            # Para dicionários dentro da lista (ex: erros)
                            item_dict = {}
                            for k, v in item.items():
                                k_traduzido = {
                                    'situation': 'situacao',
                                    'reason': 'motivo'
                                }.get(k, k)
                                if isinstance(v, Situation):
                                    item_dict[k_traduzido] = self._serialize_situation(v)
                                else:
                                    item_dict[k_traduzido] = v
                            serialized[key_traduzido].append(item_dict)
                        else:
                            serialized[key_traduzido].append(item)
                elif isinstance(value, dict):
                    # Para dicionários (ex: dep_graph)
                    serialized[key_traduzido] = {}
                    for k, v in value.items():
                        if isinstance(v, list):
                            serialized[key_traduzido][k] = v
                        else:
                            serialized[key_traduzido][k] = v
                else:
                    # Para valores simples
                    serialized[key_traduzido] = value
            return serialized
        else:
            return str(validation_result) if hasattr(validation_result, '__dict__') else validation_result
    
    def save_results(self, summary):
        """Save processing results to JSON file."""
        # Sanitizar resultados de validação e acurácia antes de salvar
        for result in summary.get('detailed_results', []):
            if 'validation_result' in result:
                result['validation_result'] = self._serialize_validation_result(result['validation_result'])
            if 'heuristic_accuracy' in result:
                result['heuristic_accuracy'] = self._serialize_heuristic_accuracy(result['heuristic_accuracy'])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_folder / f"batch_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            # Use custom encoder to handle Situation objects
            json.dump(summary, f, indent=2, ensure_ascii=False, cls=SituationEncoder)
        
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Total files: {summary['batch_info']['total_files']}")
        print(f"Successful: {summary['batch_info']['successful']}")
        print(f"Failed: {summary['batch_info']['failed']}")
        print(f"Total batch time: {summary['batch_info']['batch_total_time']:.2f}s")
        
        if summary['time_statistics']:
            print(f"\nTime Statistics (successful runs):")
            for key, stats in summary['time_statistics'].items():
                print(f"  {key}:")
                print(f"    Min: {stats['min']:.2f}s | Max: {stats['max']:.2f}s | Avg: {stats['avg']:.2f}s")
        
        if summary['batch_info']['failed'] > 0:
            print(f"\nFailed files:")
            for result in self.processing_results:
                if not result['success']:
                    print(f"  - {result['relative_path']}: {result['error']}")
        
        print(f"\nResults saved to: {results_file}")
        
        return results_file
    
    def generate_performance_graphs(self, summary):
        """Generate performance visualization graphs."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Time breakdown by stage (bar chart)
        ax1 = plt.subplot(2, 3, 1)
        if summary['time_statistics']:
            stages = list(summary['time_statistics'].keys())
            avg_times = [summary['time_statistics'][s]['avg'] for s in stages]
            colors = plt.cm.viridis(np.linspace(0, 1, len(stages)))
            ax1.bar(stages, avg_times, color=colors)
            ax1.set_ylabel('Time (seconds)')
            ax1.set_title('Average Processing Time by Stage')
            ax1.tick_params(axis='x', rotation=45)
        
        # 2. Min/Max/Avg comparison (box plot style)
        ax2 = plt.subplot(2, 3, 2)
        if summary['time_statistics']:
            stages = list(summary['time_statistics'].keys())
            data_to_plot = [
                [summary['time_statistics'][s]['min'],
                 summary['time_statistics'][s]['avg'],
                 summary['time_statistics'][s]['max']]
                for s in stages
            ]
            data_to_plot = list(zip(*data_to_plot))
            x = np.arange(len(stages))
            width = 0.25
            ax2.bar(x - width, data_to_plot[0], width, label='Min', alpha=0.8)
            ax2.bar(x, data_to_plot[1], width, label='Avg', alpha=0.8)
            ax2.bar(x + width, data_to_plot[2], width, label='Max', alpha=0.8)
            ax2.set_ylabel('Time (seconds)')
            ax2.set_title('Time Statistics by Stage')
            ax2.set_xticks(x)
            ax2.set_xticklabels(stages, rotation=45)
            ax2.legend()
        
        # 3. Processing time per file
        ax3 = plt.subplot(2, 3, 3)
        successful_results = [r for r in self.processing_results if r['success']]
        if successful_results:
            file_names = [Path(r['relative_path']).stem for r in successful_results]
            total_times = [r['times']['total'] for r in successful_results]
            colors_files = ['green' if t < np.mean(total_times) else 'orange' if t < np.max(total_times) else 'red' 
                           for t in total_times]
            ax3.barh(file_names, total_times, color=colors_files)
            ax3.set_xlabel('Time (seconds)')
            ax3.set_title('Total Processing Time per File')
            ax3.axvline(np.mean(total_times), color='red', linestyle='--', label='Average')
            ax3.legend()
        
        # 4. Success rate pie chart
        ax4 = plt.subplot(2, 3, 4)
        successful = summary['batch_info']['successful']
        failed = summary['batch_info']['failed']
        sizes = [successful, failed]
        labels = [f'Successful\n({successful})', f'Failed\n({failed})']
        colors_pie = ['#90EE90', '#FFB6C6']
        ax4.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
        ax4.set_title('Processing Success Rate')
        
        # 5. Stage breakdown for total time (stacked bar)
        ax5 = plt.subplot(2, 3, 5)
        if successful_results:
            file_names = [Path(r['relative_path']).stem for r in successful_results]
            load_times = [r['times'].get('load_log', 0) for r in successful_results]
            layer1_times = [r['times'].get('layer1_mining', 0) for r in successful_results]
            sbmn_times = [r['times'].get('sbmn_mining', 0) for r in successful_results]
            val_times = [r['times'].get('validation', 0) for r in successful_results]
            json_times = [r['times'].get('json_generation', 0) for r in successful_results]
            
            x = np.arange(len(file_names))
            width = 0.6
            
            ax5.bar(x, load_times, width, label='Load Log', color='#FF9999')
            ax5.bar(x, layer1_times, width, bottom=load_times, label='Layer1 Mining', color='#66B2FF')
            ax5.bar(x, sbmn_times, width, bottom=np.array(load_times)+np.array(layer1_times), label='SBMN Mining', color='#99FF99')
            ax5.bar(x, val_times, width, bottom=np.array(load_times)+np.array(layer1_times)+np.array(sbmn_times), label='Validation', color='#FFCC99')
            ax5.bar(x, json_times, width, bottom=np.array(load_times)+np.array(layer1_times)+np.array(sbmn_times)+np.array(val_times), label='JSON Gen', color='#FF99CC')
            
            ax5.set_ylabel('Time (seconds)')
            ax5.set_title('Processing Time Breakdown per File')
            ax5.set_xticks(x)
            ax5.set_xticklabels(file_names, rotation=45, ha='right')
            ax5.legend(loc='upper left', fontsize=8)
        
        # 6. Constraints and model size
        ax6 = plt.subplot(2, 3, 6)
        if successful_results:
            file_names = [Path(r['relative_path']).stem for r in successful_results]
            layer1_counts = [r.get('layer1_constraints_count', 0) for r in successful_results]
            sbmn_sizes = [r.get('sbmn_model_size', 0) for r in successful_results]
            
            x = np.arange(len(file_names))
            width = 0.35
            
            ax6_2 = ax6.twinx()
            bars1 = ax6.bar(x - width/2, layer1_counts, width, label='Layer1 Constraints', color='#FF9999', alpha=0.8)
            bars2 = ax6_2.bar(x + width/2, sbmn_sizes, width, label='SBMN Elements', color='#99FF99', alpha=0.8)
            
            ax6.set_xlabel('File')
            ax6.set_ylabel('Constraints Count', color='#FF9999')
            ax6_2.set_ylabel('Model Size', color='#99FF99')
            ax6.set_title('Constraints and Model Size')
            ax6.set_xticks(x)
            ax6.set_xticklabels(file_names, rotation=45, ha='right')
            ax6.tick_params(axis='y', labelcolor='#FF9999')
            ax6_2.tick_params(axis='y', labelcolor='#99FF99')
            
            # Combine legends
            lines1, labels1 = ax6.get_legend_handles_labels()
            lines2, labels2 = ax6_2.get_legend_handles_labels()
            ax6.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)
        
        plt.tight_layout()
        
        # Save figure
        graph_file = self.output_folder / f"performance_graphs_{timestamp}.png"
        plt.savefig(graph_file, dpi=300, bbox_inches='tight')
        print(f"\n Performance graphs saved to: {graph_file}")
        
        # Also save individual graphs for better clarity
        self._save_individual_graphs(summary, timestamp)
        
        plt.close()
        return graph_file
    
    def _save_individual_graphs(self, summary, timestamp):
        """Save individual detailed graphs."""
        
        # Graph 1: Timeline comparison
        fig, ax = plt.subplots(figsize=(12, 6))
        successful_results = [r for r in self.processing_results if r['success']]
        if successful_results:
            file_names = [Path(r['relative_path']).stem for r in successful_results]
            total_times = [r['times']['total'] for r in successful_results]
            colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.7, len(file_names)))
            bars = ax.bar(file_names, total_times, color=colors, edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar, time in zip(bars, total_times):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{time:.2f}s', ha='center', va='bottom', fontsize=9)
            
            ax.set_ylabel('Time (seconds)', fontsize=12)
            ax.set_xlabel('Files', fontsize=12)
            ax.set_title('Total Processing Time per File (Detailed)', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            graph_file = self.output_folder / f"timeline_comparison_{timestamp}.png"
            plt.savefig(graph_file, dpi=300, bbox_inches='tight')
            plt.close()
    
    def generate_performance_report_table(self, summary):
        """Generate a formatted text table with performance results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_folder / f"performance_report_{timestamp}.txt"
        
        successful_results = [r for r in self.processing_results if r['success']]
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 150 + "\n")
            f.write("BATCH PROCESSING PERFORMANCE REPORT\n")
            f.write("=" * 150 + "\n\n")
            
            # Batch Summary
            f.write("BATCH SUMMARY\n")
            f.write("-" * 150 + "\n")
            f.write(f"{'Main Folder:':<30} {self.main_folder}\n")
            f.write(f"{'Output Folder:':<30} {self.output_folder}\n")
            f.write(f"{'Generated:':<30} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'Total Files:':<30} {summary['batch_info']['total_files']}\n")
            f.write(f"{'Successful:':<30} {summary['batch_info']['successful']}\n")
            f.write(f"{'Failed:':<30} {summary['batch_info']['failed']}\n")
            f.write(f"{'Total Batch Time:':<30} {summary['batch_info']['batch_total_time']:.2f}s\n")
            f.write(f"{'Success Rate:':<30} {(summary['batch_info']['successful']/summary['batch_info']['total_files']*100):.1f}%\n\n")
            
            # Mining Parameters
            f.write("MINING PARAMETERS\n")
            f.write("-" * 150 + "\n")
            f.write(f"{'Min Support Layer 1:':<30} {summary['mining_parameters']['min_support_layer1']}\n")
            f.write(f"{'Min Support Layer 2:':<30} {summary['mining_parameters']['min_support_layer2']}\n")
            f.write(f"{'Itemsets Support Layer 1:':<30} {summary['mining_parameters']['itemsets_support_layer1']}\n")
            f.write(f"{'Itemsets Support Layer 2:':<30} {summary['mining_parameters']['itemsets_support_layer2']}\n\n")
            
            # Performance Table
            f.write("DETAILED PERFORMANCE TABLE\n")
            f.write("-" * 200 + "\n")
            
            # Table header
            f.write(f"{'File':<30} {'Status':<10} {'Total':<10} {'Load':<10} {'Layer1':<10} {'SBMN':<10} {'Inductive':<12} {'Alpha':<10} {'Valid':<10} {'JSON':<10}\n")
            f.write(f"{'(seconds)':<30} {'':<10} {'(s)':<10} {'(s)':<10} {'(s)':<10} {'(s)':<10} {'(s)':<12} {'(s)':<10} {'(s)':<10} {'(s)':<10}\n")
            f.write("-" * 200 + "\n")
            
            # Data rows
            for result in self.processing_results:
                file_name = Path(result['relative_path']).stem[:28]
                status = "OK" if result['success'] else "FAIL"
                
                if result['success']:
                    total_time = f"{result['times'].get('total', 0):.2f}"
                    load_time = f"{result['times'].get('load_log', 0):.2f}"
                    layer1_time = f"{result['times'].get('layer1_mining', 0):.2f}"
                    sbmn_time = f"{result['times'].get('sbmn_mining', 0):.2f}"
                    inductive_time = f"{result['times'].get('inductive_miner', 0):.2f}"
                    alpha_time = f"{result['times'].get('alpha_miner', 0):.2f}"
                    valid_time = f"{result['times'].get('validation', 0):.2f}"
                    json_time = f"{result['times'].get('json_generation', 0):.2f}"
                else:
                    total_time = "N/A"
                    load_time = "N/A"
                    layer1_time = "N/A"
                    sbmn_time = "N/A"
                    inductive_time = "N/A"
                    alpha_time = "N/A"
                    valid_time = "N/A"
                    json_time = "N/A"
                
                f.write(f"{file_name:<30} {status:<10} {total_time:<10} {load_time:<10} {layer1_time:<10} {sbmn_time:<10} {inductive_time:<12} {alpha_time:<10} {valid_time:<10} {json_time:<10}\n")
            
            f.write("-" * 200 + "\n\n")
            
            # Statistics Summary
            if summary['time_statistics']:
                f.write("TIME STATISTICS (Successful Runs)\n")
                f.write("-" * 150 + "\n")
                f.write(f"{'Stage':<25} {'Min (s)':<15} {'Max (s)':<15} {'Avg (s)':<15} {'Total (s)':<15}\n")
                f.write("-" * 150 + "\n")
                
                for stage, stats in summary['time_statistics'].items():
                    f.write(f"{stage:<25} {stats['min']:<15.2f} {stats['max']:<15.2f} {stats['avg']:<15.2f} {stats['total']:<15.2f}\n")
                
                f.write("\n")
            
            # Constraints and Model Size
            if successful_results:
                f.write("MINING RESULTS\n")
                f.write("-" * 150 + "\n")
                f.write(f"{'File':<30} {'Layer1 Constraints':<20} {'SBMN Model Size':<20}\n")
                f.write("-" * 150 + "\n")
                
                for result in successful_results:
                    file_name = Path(result['relative_path']).stem[:28]
                    constraints = result.get('layer1_constraints_count', 0)
                    sbmn_size = result.get('sbmn_model_size', 0)
                    f.write(f"{file_name:<30} {constraints:<20} {sbmn_size:<20}\n")
                
                f.write("\n")
            
            # Failed files
            if summary['batch_info']['failed'] > 0:
                f.write("FAILED FILES\n")
                f.write("-" * 150 + "\n")
                
                for result in self.processing_results:
                    if not result['success']:
                        file_name = Path(result['relative_path']).stem
                        error = result['error']
                        f.write(f"File: {file_name}\n")
                        f.write(f"Error: {error}\n\n")
        
        print(f"\ Performance report saved to: {report_file}")
        return report_file
    
    def generate_validation_report_table(self, summary):
        """Generate a formatted text table with validation assertion test results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_folder / f"validation_report_{timestamp}.txt"
        
        successful_results = [r for r in self.processing_results if r['success'] and r.get('validation_result')]
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 150 + "\n")
            f.write("SBMN MODEL VALIDATION REPORT - ASSERTION TESTS\n")
            f.write("=" * 150 + "\n\n")
            
            # Summary
            f.write("VALIDATION SUMMARY\n")
            f.write("-" * 150 + "\n")
            f.write(f"{'Generated:':<30} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'Files with Validation:':<30} {len(successful_results)}\n\n")
            
            # Process each file's validation results
            for idx, result in enumerate(successful_results, 1):
                file_name = Path(result['relative_path']).stem
                validation = result.get('validation_result', {})
                
                f.write("=" * 150 + "\n")
                f.write(f"FILE {idx}: {file_name}\n")
                f.write("=" * 150 + "\n")
                
                if isinstance(validation, dict):
                    # Extract validation data
                    total_tests = validation.get('total_tests', 0)
                    passed_tests = validation.get('passed_tests', 0)
                    failed_tests = validation.get('failed_tests', 0)
                    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
                    
                    f.write(f"{'Total Assertion Tests:':<40} {total_tests}\n")
                    f.write(f"{'Passed Tests:':<40} {passed_tests}\n")
                    f.write(f"{'Failed Tests:':<40} {failed_tests}\n")
                    f.write(f"{'Success Rate:':<40} {success_rate:.1f}%\n")
                    
                    # Test categories if available
                    if 'test_categories' in validation:
                        f.write(f"\n{'Test Categories:':<40}\n")
                        f.write("-" * 150 + "\n")
                        for category, count in validation['test_categories'].items():
                            f.write(f"  {category:<38} {count}\n")
                    
                    # Detailed test results if available
                    if 'tests' in validation and validation['tests']:
                        f.write(f"\n{'Detailed Test Results:':<40}\n")
                        f.write("-" * 150 + "\n")
                        f.write(f"{'Test Name':<50} {'Status':<15} {'Details':<80}\n")
                        f.write("-" * 150 + "\n")
                        
                        for test in validation['tests']:
                            test_name = test.get('name', 'Unknown')[:48]
                            test_status = "PASS" if test.get('passed', False) else "FAIL"
                            test_details = test.get('details', '')[:78]
                            f.write(f"{test_name:<50} {test_status:<15} {test_details:<80}\n")
                    
                    # Failed assertions if available
                    if 'failed_assertions' in validation and validation['failed_assertions']:
                        f.write(f"\n{'Failed Assertions:':<40}\n")
                        f.write("-" * 150 + "\n")
                        
                        for assertion in validation['failed_assertions']:
                            f.write(f"  - {assertion}\n")
                else:
                    # If validation is just a boolean or simple result
                    f.write(f"{'Validation Result:':<40} {'PASSED' if validation else 'FAILED'}\n")
                
                f.write("\n")
            
            f.write("=" * 150 + "\n")
            f.write(f"END OF VALIDATION REPORT\n")
            f.write("=" * 150 + "\n")
        
        print(f" Validation report saved to: {report_file}")
        return report_file
    
    def generate_combined_report(self, summary):
        """Generate a combined report with both performance and validation results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_folder / f"combined_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 150 + "\n")
            f.write("COMBINED PERFORMANCE & VALIDATION REPORT\n")
            f.write("=" * 150 + "\n\n")
            
            # Batch Info
            f.write("BATCH INFORMATION\n")
            f.write("-" * 150 + "\n")
            f.write(f"{'Timestamp:':<40} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'Main Folder:':<40} {self.main_folder}\n")
            f.write(f"{'Total Files Processed:':<40} {summary['batch_info']['total_files']}\n")
            f.write(f"{'Successful:':<40} {summary['batch_info']['successful']}\n")
            f.write(f"{'Failed:':<40} {summary['batch_info']['failed']}\n")
            f.write(f"{'Total Batch Time:':<40} {summary['batch_info']['batch_total_time']:.2f}s\n")
            f.write(f"{'Success Rate:':<40} {(summary['batch_info']['successful']/summary['batch_info']['total_files']*100):.1f}%\n\n")
            
            # Combined Results Table
            f.write("COMBINED RESULTS TABLE\n")
            f.write("-" * 150 + "\n")
            f.write(f"{'File':<25} {'Status':<8} {'Total Time':<12} {'Validation':<15} {'Passed Tests':<15} {'Success %':<12}\n")
            f.write(f"{'':25} {'':8} {'(s)':12} {'Status':15} {'Count':15} {'':12}\n")
            f.write("-" * 150 + "\n")
            
            for result in self.processing_results:
                file_name = Path(result['relative_path']).stem[:23]
                status = " OK" if result['success'] else " FAIL"
                
                if result['success']:
                    total_time = f"{result['times'].get('total', 0):.2f}"
                    validation = result.get('validation_result', {})
                    
                    if isinstance(validation, dict):
                        val_status = "PASSED" if validation.get('failed_tests', 0) == 0 else "FAILED"
                        passed = validation.get('passed_tests', 0)
                        total = validation.get('total_tests', 1)
                        success_rate = f"{(passed/total*100):.1f}%"
                    else:
                        val_status = "PASSED" if validation else "FAILED"
                        passed = "N/A"
                        success_rate = "N/A"
                else:
                    total_time = "N/A"
                    val_status = "N/A"
                    passed = "N/A"
                    success_rate = "N/A"
                
                f.write(f"{file_name:<25} {status:<8} {total_time:<12} {val_status:<15} {str(passed):<15} {success_rate:<12}\n")
            
            f.write("-" * 150 + "\n\n")
            
            # Summary Statistics
            successful_results = [r for r in self.processing_results if r['success']]
            
            if successful_results:
                f.write("SUMMARY STATISTICS\n")
                f.write("-" * 150 + "\n")
                
                total_times = [r['times'].get('total', 0) for r in successful_results]
                avg_time = sum(total_times) / len(total_times) if total_times else 0
                min_time = min(total_times) if total_times else 0
                max_time = max(total_times) if total_times else 0
                
                f.write(f"{'Average Processing Time:':<40} {avg_time:.2f}s\n")
                f.write(f"{'Minimum Processing Time:':<40} {min_time:.2f}s\n")
                f.write(f"{'Maximum Processing Time:':<40} {max_time:.2f}s\n")
                
                # Validation statistics
                validations = [r.get('validation_result', {}) for r in successful_results if isinstance(r.get('validation_result'), dict)]
                if validations:
                    total_passed = sum(v.get('passed_tests', 0) for v in validations)
                    total_tests_run = sum(v.get('total_tests', 0) for v in validations)
                    overall_rate = (total_passed / total_tests_run * 100) if total_tests_run > 0 else 0
                    
                    f.write(f"\n{'Overall Validation Statistics:':<40}\n")
                    f.write(f"{'Total Assertion Tests Run:':<40} {total_tests_run}\n")
                    f.write(f"{'Total Tests Passed:':<40} {total_passed}\n")
                    f.write(f"{'Overall Success Rate:':<40} {overall_rate:.1f}%\n")
                
                # Heuristic Accuracy Statistics
                accuracy_results = [r.get('heuristic_accuracy', {}) for r in successful_results if r.get('heuristic_accuracy')]
                if accuracy_results:
                    # Calcular totais
                    total_acertos = 0
                    total_erros = 0
                    
                    for acc_dict in accuracy_results:
                        for relation_type, metrics in acc_dict.items():
                            if isinstance(metrics, dict):
                                total_acertos += metrics.get('acertos', 0)
                                total_erros += metrics.get('erros', 0)
                    
                    total_heuristica = total_acertos + total_erros
                    if total_heuristica > 0:
                        taxa_acerto = (total_acertos / total_heuristica) * 100
                    else:
                        taxa_acerto = 0
                    
                    f.write(f"\n{'Heuristic Accuracy Statistics:':<40}\n")
                    f.write(f"{'Total Heuristic Predictions:':<40} {total_heuristica}\n")
                    f.write(f"{'Total Correct (Acertos):':<40} {total_acertos}\n")
                    f.write(f"{'Total Wrong (Erros):':<40} {total_erros}\n")
                    f.write(f"{'Overall Accuracy Rate:':<40} {taxa_acerto:.1f}%\n")
            
            f.write("\n" + "=" * 150 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 150 + "\n")
        
        print(f" Combined report saved to: {report_file}")
        return report_file
    
    def generate_folder_statistics_report(self, summary):
        """Generate statistics report grouped by folder (Mean and Std Dev)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_folder / f"folder_statistics_report_{timestamp}.txt"
        
        successful_results = [r for r in self.processing_results if r['success']]
        
        if not successful_results:
            print("No successful results to generate statistics.")
            return None
        
        # Group results by folder
        folder_groups = defaultdict(list)
        for result in successful_results:
            folder_name = Path(result['relative_path']).parent
            if not folder_name.as_posix() or folder_name.as_posix() == '.':
                folder_name = Path('root')
            folder_groups[str(folder_name)].append(result)
        
        # Prepare data for DataFrame
        rows = []
        for folder_idx, (folder_name, results) in enumerate(sorted(folder_groups.items()), start=1):
            # Extract metrics
            total_times = [r['times'].get('total', 0) for r in results]
            load_times = [r['times'].get('load_log', 0) for r in results]
            layer1_times = [r['times'].get('layer1_mining', 0) for r in results]
            sbmn_times = [r['times'].get('sbmn_mining', 0) for r in results]
            inductive_times = [r['times'].get('inductive_miner', 0) for r in results]
            alpha_times = [r['times'].get('alpha_miner', 0) for r in results]
            validation_times = [r['times'].get('validation', 0) for r in results]
            json_times = [r['times'].get('json_generation', 0) for r in results]
            
            # Heuristic accuracy metrics
            accuracy_values = []
            for r in results:
                acc_summary = r.get('heuristic_accuracy', {})
                if acc_summary:
                    total_acertos = 0
                    total_erros = 0
                    for relation_type, metrics in acc_summary.items():
                        if isinstance(metrics, dict):
                            total_acertos += metrics.get('acertos', 0)
                            total_erros += metrics.get('erros', 0)
                    total = total_acertos + total_erros
                    if total > 0:
                        accuracy_values.append((total_acertos / total) * 100)
            
            # Validation metrics
            validation_values = []
            for r in results:
                val = r.get('validation_result', {})
                if isinstance(val, dict) and val.get('total_tests', 0) > 0:
                    passed = val.get('passed_tests', 0)
                    total = val.get('total_tests', 1)
                    validation_values.append((passed / total) * 100)
            
            # Constraints and model size
            constraints = [r.get('layer1_constraints_count', 0) for r in results]
            sbmn_sizes = [r.get('sbmn_model_size', 0) for r in results]
            
            # Create row with statistics
            row = {
                'Folder Index': folder_idx,
                'Folder Name': folder_name,
                'File Count': len(results),
                'Total Time Mean': round(np.mean(total_times), 2) if total_times else 0,
                'Total Time Std': round(np.std(total_times), 2) if total_times else 0,
                'Load Time Mean': round(np.mean(load_times), 2) if load_times else 0,
                'Load Time Std': round(np.std(load_times), 2) if load_times else 0,
                'Layer1 Time Mean': round(np.mean(layer1_times), 2) if layer1_times else 0,
                'Layer1 Time Std': round(np.std(layer1_times), 2) if layer1_times else 0,
                'SBMN Time Mean': round(np.mean(sbmn_times), 2) if sbmn_times else 0,
                'SBMN Time Std': round(np.std(sbmn_times), 2) if sbmn_times else 0,
                'Inductive Time Mean': round(np.mean(inductive_times), 2) if inductive_times else 0,
                'Inductive Time Std': round(np.std(inductive_times), 2) if inductive_times else 0,
                'Alpha Time Mean': round(np.mean(alpha_times), 2) if alpha_times else 0,
                'Alpha Time Std': round(np.std(alpha_times), 2) if alpha_times else 0,
                'Validation Time Mean': round(np.mean(validation_times), 2) if validation_times else 0,
                'Validation Time Std': round(np.std(validation_times), 2) if validation_times else 0,
                'Heuristic Accuracy Mean': round(np.mean(accuracy_values), 2) if accuracy_values else 0,
                'Heuristic Accuracy Std': round(np.std(accuracy_values), 2) if accuracy_values else 0,
                'Validation Success Mean': round(np.mean(validation_values), 2) if validation_values else 0,
                'Validation Success Std': round(np.std(validation_values), 2) if validation_values else 0,
                'Constraints Mean': round(np.mean(constraints), 1) if constraints else 0,
                'Constraints Std': round(np.std(constraints), 1) if constraints else 0,
                'SBMN Size Mean': round(np.mean(sbmn_sizes), 1) if sbmn_sizes else 0,
                'SBMN Size Std': round(np.std(sbmn_sizes), 1) if sbmn_sizes else 0,
            }
            rows.append(row)
        
        # Create DataFrame and print
        df = pd.DataFrame(rows)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 250 + "\n")
            f.write("FOLDER STATISTICS REPORT (Mean and Standard Deviation)\n")
            f.write("=" * 200 + "\n\n")
            
            f.write(df.to_string(index=False))
            f.write("\n\n" + "=" * 200 + "\n")
        
        # Also print to console
        print("\n" + "=" * 250)
        print("FOLDER STATISTICS REPORT (Mean and Standard Deviation)")
        print("=" * 250)
        print(df.to_string(index=False))
        print("=" * 250)
        
        print(f"\n Folder statistics report saved to: {report_file}")
        return report_file


def main():
    """Main entry point for batch processing."""
    
    # Configuration
    # MAIN_FOLDER = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXPERIMENTOS"  # Change to your main folder
    # MAIN_FOLDER = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXPERIMENTOS/ComputerRepair_1"  # Change to your main folder
    # MAIN_FOLDER = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXPERIMENTOS/SELECAO"  # Change to your main folder
    MAIN_FOLDER = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXPERIMENTOS2"  # Change to your main folder
    OUTPUT_FOLDER = "OUTPUTS"
    
    # Mining parameters
    MIN_SUPPORT_LAYER1 = 0.6
    MIN_SUPPORT_LAYER2 = 0.1
    ITEMSETS_SUPPORT_LAYER1 = 0.01
    ITEMSETS_SUPPORT_LAYER2 = 0.00001
    
    # Create processor
    processor = BatchProcessor(
        main_folder=MAIN_FOLDER,
        output_folder=OUTPUT_FOLDER,
        min_support_layer1=MIN_SUPPORT_LAYER1,
        min_support_layer2=MIN_SUPPORT_LAYER2,
        itemsets_support_layer1=ITEMSETS_SUPPORT_LAYER1,
        itemsets_support_layer2=ITEMSETS_SUPPORT_LAYER2
    )
    
    # Process all files
    summary = processor.process_all_files()
    
    print("\n Batch processing completed!")


if __name__ == "__main__":
    main()
