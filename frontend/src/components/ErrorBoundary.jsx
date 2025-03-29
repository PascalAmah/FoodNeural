import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      errorMessage: null,
    };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      errorMessage: error?.message || "An unexpected error occurred",
    };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Component Error:", {
      error: error?.message,
      componentStack: errorInfo?.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-red-800 font-medium">Something went wrong</h3>
          <p className="text-red-600">
            {this.state.errorMessage || "Unable to display impact data"}
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
