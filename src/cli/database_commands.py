"""
CLI commands for database management

This module provides command-line utilities for managing the database,
including seeding data, health checks, and maintenance operations.
"""

import click
from flask.cli import with_appcontext
from src.database.seed_data import seed_all_data, clear_all_data
from src.database.health_check import get_database_health
import json

@click.command()
@with_appcontext
def seed_db():
    """Seed the database with sample data for development and testing."""
    try:
        click.echo("Seeding database with sample data...")
        results = seed_all_data()
        click.echo(f"✅ Database seeded successfully!")
        click.echo(f"Created: {results['customers']} customers, {results['crew_members']} crew members, "
                  f"{results['crews']} crews, {results['appointments']} appointments")
    except Exception as e:
        click.echo(f"❌ Error seeding database: {str(e)}", err=True)
        raise click.Abort()

@click.command()
@with_appcontext
def clear_db():
    """Clear all data from the database (use with caution!)."""
    if click.confirm('⚠️  This will delete ALL data from the database. Are you sure?'):
        try:
            click.echo("Clearing database...")
            clear_all_data()
            click.echo("✅ Database cleared successfully!")
        except Exception as e:
            click.echo(f"❌ Error clearing database: {str(e)}", err=True)
            raise click.Abort()
    else:
        click.echo("Operation cancelled.")

@click.command()
@with_appcontext
def health_check():
    """Run comprehensive database health checks."""
    try:
        click.echo("Running database health checks...")
        health_report = get_database_health()
        
        # Display overall status
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'unhealthy': '❌'
        }
        
        click.echo(f"\n{status_emoji.get(health_report['overall_status'], '❓')} Overall Status: {health_report['overall_status'].upper()}")
        click.echo(f"Timestamp: {health_report['timestamp']}")
        
        # Display individual check results
        click.echo("\nDetailed Results:")
        for check_name, result in health_report['checks'].items():
            emoji = status_emoji.get(result['status'], '❓')
            click.echo(f"  {emoji} {check_name.replace('_', ' ').title()}: {result['status']} - {result['message']}")
        
        # Display summary
        summary = health_report['summary']
        click.echo(f"\nSummary: {summary['healthy']} healthy, {summary['warnings']} warnings, {summary['unhealthy']} unhealthy")
        
        # Exit with appropriate code
        if health_report['overall_status'] == 'unhealthy':
            raise click.Abort()
            
    except Exception as e:
        click.echo(f"❌ Error running health checks: {str(e)}", err=True)
        raise click.Abort()

@click.command()
@with_appcontext
def health_json():
    """Output database health check results in JSON format."""
    try:
        health_report = get_database_health()
        click.echo(json.dumps(health_report, indent=2))
    except Exception as e:
        error_report = {
            'overall_status': 'unhealthy',
            'error': str(e),
            'timestamp': None
        }
        click.echo(json.dumps(error_report, indent=2))
        raise click.Abort()

@click.command()
@with_appcontext
def init_db():
    """Initialize the database with tables."""
    try:
        from src.models.user import db
        click.echo("Initializing database...")
        db.create_all()
        click.echo("✅ Database initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Error initializing database: {str(e)}", err=True)
        raise click.Abort()

@click.command()
@with_appcontext
def reset_db():
    """Reset the database (clear and re-initialize)."""
    if click.confirm('⚠️  This will reset the entire database. Are you sure?'):
        try:
            click.echo("Resetting database...")
            
            # Clear all data
            clear_all_data()
            click.echo("✅ Data cleared")
            
            # Re-initialize tables
            from src.models.user import db
            db.create_all()
            click.echo("✅ Tables re-created")
            
            click.echo("✅ Database reset successfully!")
        except Exception as e:
            click.echo(f"❌ Error resetting database: {str(e)}", err=True)
            raise click.Abort()
    else:
        click.echo("Operation cancelled.")

def register_commands(app):
    """Register all database commands with the Flask app."""
    app.cli.add_command(seed_db)
    app.cli.add_command(clear_db)
    app.cli.add_command(health_check)
    app.cli.add_command(health_json)
    app.cli.add_command(init_db)
    app.cli.add_command(reset_db)

