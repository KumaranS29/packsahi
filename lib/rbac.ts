export const ROLES = ['SUPER_ADMIN','CONTROLLER','INSPECTOR','BRAND_QA','CITIZEN','VIEWER'] as const
export type Role = typeof ROLES[number]
export const permissions: Record<Role, string[]> = {
 SUPER_ADMIN: ['*'], CONTROLLER: ['dashboard:view','scan:view:all','scan:create','users:manage','reports:generate','notices:create','form_a:approve'], INSPECTOR: ['scan:create','scan:view:own','reports:generate','notices:view','notices:create','form_a:draft','scan:offline'], BRAND_QA: ['scan:view:brand','reports:brand','artwork:upload','artwork:verify','brand:audit','brand:certificate'], CITIZEN: ['scan:basic','scan:create:consumer','repository:public','grievance:create','grievance:view:own'], VIEWER: ['scan:view:public','reports:view:public','dashboard:view:public']
}
export function hasPermission(role: Role, permission: string) { return permissions[role]?.includes('*') || permissions[role]?.includes(permission) }
export function assertRole(value: string): Role { return (ROLES as readonly string[]).includes(value) ? value as Role : 'VIEWER' }
