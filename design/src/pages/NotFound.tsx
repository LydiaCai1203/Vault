export default function NotFound() {
  return (
    <div className="min-h-screen bg-background text-foreground grid place-items-center p-8">
      <div className="text-center">
        <div className="text-2xl font-semibold">404</div>
        <div className="mt-2 text-sm text-muted-foreground">页面不存在</div>
        <a href="#/dashboard" className="mt-4 inline-block text-primary underline underline-offset-4">
          返回总览
        </a>
      </div>
    </div>
  );
}
