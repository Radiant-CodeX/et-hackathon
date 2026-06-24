import { AlertTriangle } from "lucide-react";

export default function ErrorState({ message = "Something went wrong.", onRetry }) {
  return (
    <div className="error-state" role="alert">
      <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: 1 }} />
      <div>
        <div>{message}</div>
        {onRetry && (
          <button onClick={onRetry} type="button">
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
